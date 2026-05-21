import secrets

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import io
import re
import zipfile
import xml.etree.ElementTree as ET

import pandas as pd
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email

from meal_system.api_utils import (
	create_password_reset_token,
	get_or_create_profile,
	get_or_create_meal_plan,
	json_error,
	json_success,
	parse_json_body,
	require_auth,
	serialize_user,
)
from users.models import ActiveSession, PasswordResetToken, UserProfile

import logging

logger = logging.getLogger(__name__)


User = get_user_model()


def _issue_session(user):
	token = secrets.token_urlsafe(40)
	session, _ = ActiveSession.objects.update_or_create(
		user=user,
		defaults={
			'token': token,
			'session_id': '',
			'is_active': True,
		},
	)
	return session


@csrf_exempt
def login_view(request):
	if request.method != 'POST':
		return json_error('Method not allowed', status=405)

	data = parse_json_body(request)
	email = str(data.get('email', '')).strip().lower()
	password = str(data.get('password', ''))

	logger.debug('Login attempt for email=%s', email)

	if not email or not password:
		logger.warning('Login failed: missing email or password (email=%s)', email)
		return json_error('Email and password are required')

	user = User.objects.filter(username__iexact=email).first() or User.objects.filter(email__iexact=email).first()
	logger.debug('User lookup for email=%s found=%s', email, bool(user))
	if not user:
		logger.warning('Login failed: user not found for email=%s', email)
		return json_error('Invalid email or password', status=400)

	profile = get_or_create_profile(user)
	if profile.status == UserProfile.STATUS_INACTIVE or not user.is_active:
		logger.warning('Login failed: inactive account email=%s status=%s is_active=%s', email, profile.status, user.is_active)
		return json_error('This account is inactive', status=403)

	authenticated = authenticate(request, username=user.username, password=password)
	logger.debug('Authentication result for user=%s: %s', user.username, authenticated is not None)
	if authenticated is None:
		logger.warning('Login failed: authentication backend rejected credentials for email=%s', email)
		return json_error('Invalid email or password', status=400)

	session = _issue_session(user)
	logger.info('Login success: user_id=%s session_created=%s', user.id, bool(session))
	return json_success(user=serialize_user(user, include_meal_plan=True), token=session.token)


@csrf_exempt
@require_auth()
def logout_view(request):
	if request.method != 'POST':
		return json_error('Method not allowed', status=405)

	session = getattr(request, 'api_session', None)
	if session:
		session.is_active = False
		session.save(update_fields=['is_active'])
	return json_success()


@csrf_exempt
def password_reset_request(request):
	if request.method != 'POST':
		return json_error('Method not allowed', status=405)

	data = parse_json_body(request)
	email = str(data.get('email', '')).strip().lower()
	user = User.objects.filter(username__iexact=email).first() or User.objects.filter(email__iexact=email).first()

	if user:
		token = create_password_reset_token(user)
		return json_success(message='If an account exists, a reset link was sent.', resetUrl=f'/reset-password?token={token.token}')

	return json_success(message='If an account exists, a reset link was sent.')


@csrf_exempt
def password_reset_confirm(request):
	if request.method != 'POST':
		return json_error('Method not allowed', status=405)

	data = parse_json_body(request)
	token_value = str(data.get('token', '')).strip()
	new_password = str(data.get('password', ''))

	if not token_value or len(new_password) < 8:
		return json_error('Invalid token or password too short')

	token = PasswordResetToken.objects.select_related('user').filter(token=token_value, used_at__isnull=True).first()
	if not token:
		return json_error('Invalid or expired reset token', status=400)

	if token.expires_at < timezone.now():
		return json_error('Invalid or expired reset token', status=400)

	token.user.set_password(new_password)
	token.user.save(update_fields=['password'])
	token.used_at = timezone.now()
	token.save(update_fields=['used_at'])
	ActiveSession.objects.filter(user=token.user).update(is_active=False)
	return json_success()


@csrf_exempt
@require_auth()
def change_password(request):
	if request.method != 'POST':
		return json_error('Method not allowed', status=405)

	data = parse_json_body(request)
	current_password = str(data.get('current_password', ''))
	new_password = str(data.get('new_password', ''))

	if len(new_password) < 8:
		return json_error('New password must be at least 8 characters')

	if not request.api_user.check_password(current_password):
		return json_error('Current password is incorrect')

	request.api_user.set_password(new_password)
	request.api_user.save(update_fields=['password'])
	ActiveSession.objects.filter(user=request.api_user).update(is_active=False)
	return json_success()


@csrf_exempt
@require_auth()
def session_view(request):
	if request.method == 'POST':
		data = parse_json_body(request)
		session_id = str(data.get('sessionId', '')).strip()
		if session_id:
			request.api_session.session_id = session_id
			request.api_session.save(update_fields=['session_id'])
		return json_success(activeSession=request.api_session.session_id)

	if request.method == 'GET':
		user_id = request.GET.get('userId')
		if user_id and str(request.api_user.id) != str(user_id):
			return json_error('Session does not belong to the requested user', status=403)
		return json_success(activeSession=request.api_session.session_id)

	return json_error('Method not allowed', status=405)


HEADER_ALIASES = {
	'id': {'id', 'pk', 'user id', 'userid', 'source id', 'sourceid', 'student id', 'member id'},
	'name': {
		'name',
		'full name',
		'fullname',
		'student name',
		'member name',
		'name of student',
		'student full name',
		'candidate name',
	},
	'email': {'email', 'email address', 'emailaddress', 'e-mail', 'mail', 'e mail', 'student email'},
	'phone': {
		'phone',
		'phone number',
		'phonenumber',
		'mobile',
		'telephone',
		'contact',
		'contact number',
		'mobile number',
		'tel',
	},
	'registration_number': {
		'registration number',
		'registrationnumber',
		'registration no',
		'reg no',
		'regno',
		'registration #',
		'reg #',
		'register no',
		'matric no',
		'matric number',
		'admission no',
		'admission number',
		'student no',
		'id number',
		'student id',
		'student number',
		'adm no',
		'adm number',
	},
}


def _as_text(value):
	if value is None:
		return ''
	return str(value).strip()


def _as_int(value, default=None):
	if value is None or value == '':
		return default
	try:
		return int(float(str(value).strip()))
	except Exception:
		raise ValueError('Invalid integer value')


def _as_bool(value, default=False):
	if value is None or value == '':
		return default
	if isinstance(value, bool):
		return value
	return str(value).strip().lower() in {'1', 'true', 'yes', 'y', 'on'}


def _split_name(full_name):
	parts = _as_text(full_name).split(None, 1)
	if not parts:
		return '', ''
	if len(parts) == 1:
		return parts[0], ''
	return parts[0], parts[1]


def _normalize_excel_value(value):
	if value is None or pd.isna(value):
		return ''
	return str(value).strip()


def _normalize_header(value):
	return re.sub(r'[^a-z0-9]+', '', _as_text(value).lower())


def _looks_like_email(value):
	value = _as_text(value)
	return bool(re.search(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', value))


def _looks_like_phone(value):
	value = _as_text(value)
	if not value:
		return False
	digits = re.sub(r'\D+', '', value)
	return 7 <= len(digits) <= 15 and len(digits) >= max(7, len(value) // 2)


def _looks_like_registration(value):
	value = _as_text(value)
	if not value:
		return False
	if _looks_like_email(value) or _looks_like_phone(value):
		return False
	return bool(re.search(r'[A-Za-z0-9]', value))


def _looks_like_name(value):
	value = _as_text(value)
	if not value:
		return False
	if _looks_like_email(value) or _looks_like_phone(value):
		return False
	if len(value) < 2:
		return False
	return bool(re.search(r'[A-Za-z]', value))


def _candidate_score(values, predicate):
	clean_values = [_normalize_excel_value(value) for value in values if _normalize_excel_value(value)]
	if not clean_values:
		return 0.0
	matches = sum(1 for value in clean_values if predicate(value))
	return matches / len(clean_values)


def _get_cell_text(cell, shared_strings):
	t = cell.attrib.get('t')
	if t == 's':
		v = cell.findtext('main:v', default='', namespaces=XLSX_NS)
		if v == '':
			return ''
		idx = int(v)
		if idx < 0 or idx >= len(shared_strings):
			return ''
		return shared_strings[idx].strip()
	if t == 'inlineStr':
		return ''.join(cell.itertext()).strip()
	return cell.findtext('main:v', default='', namespaces=XLSX_NS).strip()


def _row_to_cells(row, shared_strings):
	cells = {}
	for c in row.findall('main:c', XLSX_NS):
		ref = c.attrib.get('r', '')
		m = re.match(r'([A-Z]+)', ref)
		if not m:
			continue
		col = m.group(1)
		cells[col] = _get_cell_text(c, shared_strings)
	return cells


def _resolve_header_row(rows):
	best_index = None
	best_resolved = {}
	best_score = -1

	for index, row_values in enumerate(rows):
		norm = {}
		for col, text in enumerate(row_values):
			key = _normalize_header(text)
			if key:
				norm[key] = col

		resolved = {}
		for canonical, aliases in HEADER_ALIASES.items():
			for alias in aliases:
				key = _normalize_header(alias)
				if key in norm:
					resolved[canonical] = norm[key]
					break

		score = len(resolved)
		if score > best_score:
			best_index = index
			best_resolved = resolved
			best_score = score

	if best_index is None or best_score == 0:
		best_index = 0
		best_resolved = {}

	return best_index, best_resolved


def _infer_missing_columns(rows, header_index, resolved):
	used_columns = set(resolved.values())
	data_rows = rows[header_index + 1:]
	if not data_rows:
		raise ValueError('Workbook contains no data rows')

	columns = list(range(len(rows[header_index]))) if header_index < len(rows) else []
	column_values = {col: [] for col in columns}
	for row_values in data_rows:
		for col in columns:
			if col < len(row_values):
				column_values[col].append(row_values[col])

	def choose_column(predicate):
		best_col = None
		best_score = 0.0
		for col, values in column_values.items():
			if col in used_columns:
				continue
			score = _candidate_score(values, predicate)
			if score > best_score:
				best_col = col
				best_score = score
		return best_col, best_score

	for canonical, predicate in (
		('name', _looks_like_name),
		('email', _looks_like_email),
		('phone', _looks_like_phone),
		('registration_number', _looks_like_registration),
	):
		if canonical not in resolved:
			col, score = choose_column(predicate)
			if col is not None and score >= 0.5:
				resolved[canonical] = col
				used_columns.add(col)

	missing_required = [column for column in ('name', 'email', 'phone', 'registration_number') if column not in resolved]
	if missing_required:
		raise ValueError(f'Missing columns: {", ".join(missing_required)}')

	return resolved


def _read_excel_rows(uploaded_file):
	try:
		frame = pd.read_excel(uploaded_file, header=None, dtype=object, engine='openpyxl')
	except Exception as exc:
		raise ValueError('Not a valid .xlsx file') from exc

	if frame.empty:
		raise ValueError('Workbook contains no rows')

	rows = frame.fillna('').values.tolist()
	header_index, resolved = _resolve_header_row(rows[:25])
	resolved = _infer_missing_columns(rows, header_index, resolved)

	parsed = []
	for row_values in rows[header_index + 1:]:
		if not any(_normalize_excel_value(value) for value in row_values):
			continue

		entry = {}
		for canon, col_index in resolved.items():
			entry[canon] = _normalize_excel_value(row_values[col_index]) if col_index < len(row_values) else ''
		parsed.append(entry)

	return parsed


def _load_excel_rows(uploaded_file):
	return _read_excel_rows(uploaded_file)


def _send_onboarding_email(user, temporary_password, token):
	reset_url = f'{settings.FRONTEND_BASE_URL}/reset-password?token={token.token}'
	full_name = user.get_full_name() or user.username
	subject = 'Your Meal System account credentials'
	message = (
		f'Hello {full_name},\n\n'
		'Your account has been created successfully.\n\n'
		f'Email: {user.email}\n'
		f'Temporary password: {temporary_password}\n\n'
		f'Reset your password here: {reset_url}\n\n'
		'Please log in and change your password after first access.\n'
	)
	send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)


XLSX_NS = {
	'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
	'rel': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
	'pkgrel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


def _read_shared_strings(archive):
	if 'xl/sharedStrings.xml' not in archive.namelist():
		return []
	root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
	strings = []
	for si in root.findall('main:si', XLSX_NS):
		parts = [t.text or '' for t in si.findall('.//main:t', XLSX_NS)]
		strings.append(''.join(parts))
	return strings


def _resolve_sheet_path(archive):
	workbook = ET.fromstring(archive.read('xl/workbook.xml'))
	first_sheet = workbook.find('main:sheets/main:sheet', XLSX_NS)
	if first_sheet is None:
		raise ValueError('Workbook has no sheets')
	rel_id = first_sheet.attrib.get(f'{{{XLSX_NS["rel"]}}}id')
	rels = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
	for rel in rels.findall('pkgrel:Relationship', XLSX_NS):
		if rel.attrib.get('Id') == rel_id:
			target = rel.attrib.get('Target')
			return f'xl/{target.lstrip("/")}'
	raise ValueError('Could not resolve sheet path')


def _cell_text(cell, shared_strings):
	return _get_cell_text(cell, shared_strings)


@csrf_exempt
@require_auth(roles=[UserProfile.ROLE_ADMIN])
def users_list(request):
	if request.method == 'GET':
		users = User.objects.select_related('profile', 'meal_plan').order_by('id')
		
		role_filter = request.GET.get('role')
		status_filter = request.GET.get('status')
		
		if role_filter and role_filter in dict(UserProfile.ROLE_CHOICES):
			users = users.filter(profile__role=role_filter)
		
		if status_filter and status_filter in dict(UserProfile.STATUS_CHOICES):
			users = users.filter(profile__status=status_filter)
		
		return JsonResponse([serialize_user(user) for user in users], safe=False)

	return json_error('Method not allowed', status=405)


@csrf_exempt
@require_auth(roles=[UserProfile.ROLE_ADMIN])
def create_user(request):
	if request.method != 'POST':
		return json_error('Method not allowed', status=405)

	data = parse_json_body(request)

	name = str(data.get('name', '')).strip()
	email = str(data.get('email', '')).strip().lower()
	password = str(data.get('password', '')).strip()
	phone = str(data.get('phone', '')).strip()
	registration_number = str(data.get('registration_number', '')).strip()
	role = data.get('role', UserProfile.ROLE_USER)
	status = data.get('status', UserProfile.STATUS_ACTIVE)

	if not name:
		return json_error('Name is required')
	if not email:
		return json_error('Email is required')
	try:
		validate_email(email)
	except ValidationError:
		return json_error('Email is invalid')
	if not password or len(password) < 8:
		return json_error('Password must be at least 8 characters')
	if role not in dict(UserProfile.ROLE_CHOICES):
		return json_error('Invalid role', status=400)
	if status not in dict(UserProfile.STATUS_CHOICES):
		return json_error('Invalid status', status=400)

	if User.objects.filter(email__iexact=email).exists():
		return json_error('Email already exists', status=400)
	if registration_number and UserProfile.objects.filter(registration_number=registration_number).exists():
		return json_error('Registration number already exists', status=400)

	with transaction.atomic():
		first_name, last_name = _split_name(name)
		user = User(
			username=email,
			email=email,
			first_name=first_name,
			last_name=last_name,
			is_active=status == UserProfile.STATUS_ACTIVE,
		)
		user.set_password(password)
		user.save()

		profile = get_or_create_profile(user)
		profile.role = role
		profile.status = status
		profile.phone = phone
		if registration_number:
			profile.registration_number = registration_number
		profile.save()

		meal_plan = get_or_create_meal_plan(user)
		meal_plan.save()

	return json_success(user=serialize_user(user, include_meal_plan=True))


@csrf_exempt
@require_auth(roles=[UserProfile.ROLE_ADMIN])
def user_detail(request, user_id):
	user = User.objects.filter(pk=user_id).select_related('profile', 'meal_plan').first()
	if not user:
		return json_error('User not found', status=404)

	if request.method == 'GET':
		return json_success(user=serialize_user(user, include_meal_plan=True))

	if request.method == 'PATCH':
		data = parse_json_body(request)
		profile = get_or_create_profile(user)

		name = str(data.get('name', '')).strip()
		email = str(data.get('email', '')).strip().lower()
		status = data.get('status')
		role = data.get('role')

		if name:
			parts = name.split(' ', 1)
			user.first_name = parts[0]
			user.last_name = parts[1] if len(parts) > 1 else ''

		if email:
			user.email = email
			user.username = email

		if status in dict(UserProfile.STATUS_CHOICES):
			profile.status = status
			user.is_active = status == UserProfile.STATUS_ACTIVE

		if role in dict(UserProfile.ROLE_CHOICES):
			profile.role = role

		with transaction.atomic():
			user.save()
			profile.save()

		return json_success(user=serialize_user(user, include_meal_plan=True))

	if request.method == 'DELETE':
		if request.api_user.id == user.id:
			return json_error('You cannot delete your own account', status=400)
		user.delete()
		return json_success(deleted=True, userId=user_id)

	return json_error('Method not allowed', status=405)


@csrf_exempt
@require_auth(roles=[UserProfile.ROLE_ADMIN])
def send_password_reset(request, user_id):
	if request.method != 'POST':
		return json_error('Method not allowed', status=405)

	user = User.objects.filter(pk=user_id).first()
	if not user:
		return json_error('User not found', status=404)

	token = create_password_reset_token(user)
	return json_success(email=user.email, resetUrl=f'/reset-password?token={token.token}')


@csrf_exempt
@require_auth(roles=[UserProfile.ROLE_ADMIN])
def bulk_import_users(request):
	if request.method != 'POST':
		return json_error('Method not allowed', status=405)

	# Accept either a JSON payload or a file upload named 'file'/'excel'
	data = parse_json_body(request)
	access = data.get('access') or {}

	# Allow default package settings from top-level payload
	default_days_remaining = _as_int(data.get('daysRemaining') or data.get('days_remaining'), 30) or 30
	default_total_days = _as_int(data.get('totalDays') or data.get('total_days'), 30) or 30
	default_valid_until = data.get('validUntil') or data.get('valid_until')
	if default_valid_until:
		try:
			default_valid_until = datetime.fromisoformat(str(default_valid_until)).date()
		except Exception:
			return json_error('Invalid default validUntil format')

	file_obj = request.FILES.get('file') or request.FILES.get('excel') or None
	rows = []
	if file_obj:
		try:
			rows = _read_excel_rows(file_obj)
		except ValueError as exc:
			return json_error(str(exc))
	else:
		rows = data.get('users') or []

	if not rows:
		return json_error('No users were provided')

	created = 0
	skipped = 0
	errors = []
	created_users = []

	# Precompute existing values for quick duplicate checks
	emails = [(_as_text(r.get('email')) or '').lower() for r in rows if r.get('email')]
	regs = [(_as_text(r.get('registration_number') or r.get('registrationNumber')) or '') for r in rows if r.get('registration_number') or r.get('registrationNumber')]
	existing_emails = set(User.objects.filter(email__in=emails).values_list('email', flat=True))
	existing_regs = set(UserProfile.objects.filter(registration_number__in=regs).values_list('registration_number', flat=True))

	seen_emails = set()
	seen_regs = set()

	for idx, row in enumerate(rows, start=1):
		row_no = row.get('rowNumber') or idx + 1
		row_errors = []
		name = _as_text(row.get('name'))
		email = (_as_text(row.get('email')) or '').lower()
		phone = _as_text(row.get('phone'))
		registration_number = _as_text(row.get('registration_number') or row.get('registrationNumber'))

		if not name:
			row_errors.append('Name is required')
		if not email:
			row_errors.append('Email is required')
		else:
			try:
				validate_email(email)
			except ValidationError:
				row_errors.append('Email is invalid')
		if not phone:
			row_errors.append('Phone is required')
		if not registration_number:
			row_errors.append('Registration number is required')

		if email in seen_emails or email in existing_emails:
			row_errors.append('Duplicate email')
		if registration_number and (registration_number in seen_regs or registration_number in existing_regs):
			row_errors.append('Duplicate registration number')

		if row_errors:
			errors.append({'row': row_no, 'errors': row_errors})
			skipped += 1
			continue

		meal_access = row.get('access') or access or {}
		if isinstance(meal_access, str):
			try:
				meal_access = json.loads(meal_access)
			except Exception:
				meal_access = {}

		days_remaining = _as_int(row.get('daysRemaining') or row.get('days_remaining'), default_days_remaining) or default_days_remaining
		total_days = _as_int(row.get('totalDays') or row.get('total_days'), default_total_days) or default_total_days
		valid_until = row.get('validUntil') or row.get('valid_until') or default_valid_until
		if valid_until and not isinstance(valid_until, datetime):
			try:
				valid_until = datetime.fromisoformat(str(valid_until)).date()
			except Exception:
				errors.append({'row': row_no, 'errors': ['Invalid validUntil format']})
				skipped += 1
				continue

		temporary_password = secrets.token_urlsafe(10)

		with transaction.atomic():
			user = User(username=email, email=email, first_name='', last_name='', is_active=True)
			first_name, last_name = _split_name(name)
			user.first_name = first_name
			user.last_name = last_name
			user.set_password(temporary_password)
			user.save()

			profile = get_or_create_profile(user)
			profile.phone = phone
			profile.registration_number = registration_number or None
			profile.role = UserProfile.ROLE_USER
			profile.status = UserProfile.STATUS_ACTIVE
			profile.save()

			meal_plan = get_or_create_meal_plan(user)
			meal_plan.breakfast = _as_bool(meal_access.get('breakfast', meal_access.get('Breakfast', False)))
			meal_plan.lunch = _as_bool(meal_access.get('lunch', meal_access.get('Lunch', False)))
			meal_plan.dinner = _as_bool(meal_access.get('dinner', meal_access.get('Dinner', False)))
			meal_plan.days_remaining = days_remaining
			meal_plan.total_days = total_days
			meal_plan.valid_until = valid_until
			meal_plan.save()

			# create reset token and send onboarding email
			token = create_password_reset_token(user)
			try:
				_send_onboarding_email(user, temporary_password, token)
			except Exception:
				# don't fail the whole import if emailing fails
				pass

		seen_emails.add(email)
		if registration_number:
			seen_regs.add(registration_number)
		created += 1
		created_users.append(serialize_user(user, include_meal_plan=True))

	return json_success(created=created, skipped=skipped, errors=errors, users=created_users)
