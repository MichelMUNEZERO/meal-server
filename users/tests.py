from io import BytesIO
import zipfile
from urllib.parse import parse_qs, urlparse

from django.core import mail
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from meal_system.api_utils import create_password_reset_token
from users.models import ActiveSession, PasswordResetToken, UserProfile
from users.views import _load_excel_rows


def _column_name(index):
	name = ''
	while index >= 0:
		index, remainder = divmod(index, 26)
		name = chr(ord('A') + remainder) + name
		index -= 1
	return name


def _build_xlsx(rows):
	worksheet_rows = []
	for row_index, values in enumerate(rows, start=1):
		cells = []
		for column_index, value in enumerate(values):
			column = _column_name(column_index)
			cells.append(
				f'<c r="{column}{row_index}" t="inlineStr"><is><t>{value}</t></is></c>'
			)
		worksheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')

	content_types = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
		'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />'
		'<Default Extension="xml" ContentType="application/xml" />'
		'<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml" />'
		'<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml" />'
		'</Types>'
	)
	root_rels = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
		'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml" />'
		'</Relationships>'
	)
	workbook = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
		'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
		'<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1" /></sheets>'
		'</workbook>'
	)
	rels = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
		'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml" />'
		'</Relationships>'
	)
	sheet = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
		f'<sheetData>{"".join(worksheet_rows)}</sheetData>'
		'</worksheet>'
	)

	buffer = BytesIO()
	with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
		archive.writestr('[Content_Types].xml', content_types)
		archive.writestr('_rels/.rels', root_rels)
		archive.writestr('xl/workbook.xml', workbook)
		archive.writestr('xl/_rels/workbook.xml.rels', rels)
		archive.writestr('xl/worksheets/sheet1.xml', sheet)
	return buffer.getvalue()


class UserImportTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.admin = User.objects.create_user(
			username='admin@example.com',
			email='admin@example.com',
			password='password123',
			first_name='Admin',
			last_name='User',
		)
		UserProfile.objects.create(
			user=self.admin,
			role=UserProfile.ROLE_ADMIN,
			status=UserProfile.STATUS_ACTIVE,
		)
		self.session = ActiveSession.objects.create(user=self.admin, token='test-token', is_active=True)
		self.member = User.objects.create_user(
			username='member@example.com',
			email='member@example.com',
			password='password123',
			first_name='Member',
			last_name='User',
		)
		UserProfile.objects.create(
			user=self.member,
			role=UserProfile.ROLE_USER,
			status=UserProfile.STATUS_ACTIVE,
		)
		self.member_session = ActiveSession.objects.create(user=self.member, token='member-token', is_active=True)

	def test_load_excel_rows_accepts_reordered_headers(self):
		content = _build_xlsx([
			['Contact Number', 'Member Name', 'E-mail', 'Reg #'],
			['0700000000', 'Michel Example', 'michel@example.com', 'REG-001'],
		])
		rows = _load_excel_rows(SimpleUploadedFile('import.xlsx', content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))

		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]['name'], 'Michel Example')
		self.assertEqual(rows[0]['email'], 'michel@example.com')
		self.assertEqual(rows[0]['phone'], '0700000000')
		self.assertEqual(rows[0]['registration_number'], 'REG-001')

	def test_load_excel_rows_with_title_row_and_custom_headers(self):
		content = _build_xlsx([
			['Student List 2026'],
			['ID Number', 'Student Full Name', 'E Mail', 'Mobile Number'],
			['2026-001', 'Amina Yusuf', 'amina@example.com', '+250700000001'],
		])
		rows = _load_excel_rows(SimpleUploadedFile('import.xlsx', content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))

		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]['name'], 'Amina Yusuf')
		self.assertEqual(rows[0]['email'], 'amina@example.com')
		self.assertEqual(rows[0]['phone'], '+250700000001')
		self.assertEqual(rows[0]['registration_number'], '2026-001')

	@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
	def test_bulk_import_creates_account_with_complete_fields_and_email(self):
		content = _build_xlsx([
			['Member Name', 'Email Address', 'Contact Number', 'Reg #'],
			['Jane Doe', 'jane.doe@example.com', '0700000000', 'REG-123'],
		])
		file_obj = SimpleUploadedFile(
			'import.xlsx',
			content,
			content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		)

		response = self.client.post(
			'/api/users/bulk-import/',
			{'file': file_obj},
			HTTP_AUTHORIZATION=f'Bearer {self.session.token}',
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['created'], 1)
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].to, ['jane.doe@example.com'])

		user = User.objects.get(email='jane.doe@example.com')
		self.assertEqual(user.get_full_name(), 'Jane Doe')
		self.assertEqual(user.profile.phone, '0700000000')
		self.assertEqual(user.profile.registration_number, 'REG-123')

	def test_create_user_as_admin(self):
		response = self.client.post(
			'/api/users/create/',
			{'email': 'newuser@example.com', 'name': 'New User', 'password': 'securepassword123'},
			HTTP_AUTHORIZATION=f'Bearer {self.session.token}',
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		user = User.objects.get(email='newuser@example.com')
		self.assertEqual(user.get_full_name(), 'New User')
		self.assertEqual(user.profile.role, UserProfile.ROLE_USER)

	def test_create_scanner_user_as_admin(self):
		response = self.client.post(
			'/api/users/create/',
			{
				'email': 'scanner@example.com',
				'name': 'Scanner User',
				'password': 'scannerpass123',
				'phone': '0700000001',
				'registration_number': 'SCAN-001',
				'role': UserProfile.ROLE_SCANNER,
			},
			HTTP_AUTHORIZATION=f'Bearer {self.session.token}',
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		user = User.objects.get(email='scanner@example.com')
		self.assertEqual(user.profile.role, UserProfile.ROLE_SCANNER)
		self.assertEqual(user.profile.phone, '0700000001')
		self.assertEqual(user.profile.registration_number, 'SCAN-001')

	def test_create_admin_user_as_admin(self):
		response = self.client.post(
			'/api/users/create/',
			{
				'email': 'newadmin@example.com',
				'name': 'New Admin',
				'password': 'adminpass123',
				'role': UserProfile.ROLE_ADMIN,
			},
			HTTP_AUTHORIZATION=f'Bearer {self.session.token}',
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		user = User.objects.get(email='newadmin@example.com')
		self.assertEqual(user.profile.role, UserProfile.ROLE_ADMIN)

	def test_list_users_with_role_filter(self):
		scanner_user = User.objects.create_user(
			username='scanner@example.com',
			email='scanner@example.com',
			password='password123',
			first_name='Test',
			last_name='Scanner',
		)
		profile = UserProfile.objects.create(
			user=scanner_user,
			role=UserProfile.ROLE_SCANNER,
			status=UserProfile.STATUS_ACTIVE,
		)

		response = self.client.get(
			'/api/users/?role=admin',
			HTTP_AUTHORIZATION=f'Bearer {self.session.token}',
		)

		self.assertEqual(response.status_code, 200)
		users_data = response.json()
		admin_count = sum(1 for u in users_data if u['role'] == UserProfile.ROLE_ADMIN)
		self.assertGreaterEqual(admin_count, 1)

	def test_create_user_duplicate_email_fails(self):
		response = self.client.post(
			'/api/users/create/',
			{
				'email': 'admin@example.com',
				'name': 'Duplicate',
				'password': 'password123',
			},
			HTTP_AUTHORIZATION=f'Bearer {self.session.token}',
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn('already exists', response.json()['detail'])

	def test_create_user_short_password_fails(self):
		response = self.client.post(
			'/api/users/create/',
			{
				'email': 'shortpw@example.com',
				'name': 'Short PW',
				'password': 'short',
			},
			HTTP_AUTHORIZATION=f'Bearer {self.session.token}',
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn('at least 8', response.json()['detail'])

	def test_admin_can_delete_user(self):
		user_to_delete = User.objects.create_user(
			username='delete.me@example.com',
			email='delete.me@example.com',
			password='password123',
		)
		UserProfile.objects.create(
			user=user_to_delete,
			role=UserProfile.ROLE_USER,
			status=UserProfile.STATUS_ACTIVE,
		)

		response = self.client.delete(
			f'/api/users/{user_to_delete.id}/',
			HTTP_AUTHORIZATION=f'Bearer {self.session.token}',
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(User.objects.filter(id=user_to_delete.id).exists())

	def test_normal_user_cannot_list_users(self):
		response = self.client.get(
			'/api/users/',
			HTTP_AUTHORIZATION=f'Bearer {self.member_session.token}',
		)

		self.assertEqual(response.status_code, 403)

	@override_settings(
		EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
		FRONTEND_BASE_URL='https://frontend.example.com',
	)
	def test_password_reset_request_sends_email_with_frontend_link(self):
		response = self.client.post(
			'/api/auth/password-reset/',
			{'email': 'member@example.com'},
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(mail.outbox), 1)
		email = mail.outbox[0]
		self.assertEqual(email.to, ['member@example.com'])
		self.assertIn('https://frontend.example.com/reset-password?token=', email.body)
		parsed = urlparse(next(part for part in email.body.split() if 'reset-password?token=' in part))
		token = parse_qs(parsed.query)['token'][0]
		self.assertTrue(PasswordResetToken.objects.filter(token=token, user=self.member).exists())

	@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
	def test_password_reset_confirm_requires_matching_passwords(self):
		token = create_password_reset_token(self.member)
		response = self.client.post(
			'/api/auth/password-reset/confirm/',
			{
				'token': token.token,
				'new_password': 'newpassword123',
				'confirm_password': 'differentpassword123',
			},
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn('match', response.json()['detail'])
		self.member.refresh_from_db()
		self.assertTrue(self.member.check_password('password123'))

	@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
	def test_password_reset_confirm_updates_password(self):
		old_session = ActiveSession.objects.create(user=self.member, token='old-reset-session', is_active=True)
		token = create_password_reset_token(self.member)
		response = self.client.post(
			'/api/auth/password-reset/confirm/',
			{
				'token': token.token,
				'new_password': 'newpassword123',
				'confirm_password': 'newpassword123',
			},
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		token.refresh_from_db()
		self.assertIsNotNone(token.used_at)
		self.member.refresh_from_db()
		self.assertTrue(self.member.check_password('newpassword123'))
		old_session.refresh_from_db()
		self.assertFalse(old_session.is_active)
