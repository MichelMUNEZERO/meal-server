from io import BytesIO
import zipfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from users.models import ActiveSession, UserProfile
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

	def test_bulk_import_creates_account_with_optional_fields(self):
		content = _build_xlsx([
			['Member Name', 'Email Address'],
			['Jane Doe', 'jane.doe@example.com'],
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

		user = User.objects.get(email='jane.doe@example.com')
		self.assertEqual(user.get_full_name(), 'Jane Doe')
		self.assertEqual(user.profile.phone, '')
		self.assertIsNone(user.profile.registration_number)
