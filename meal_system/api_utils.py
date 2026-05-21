import hashlib
import hmac
import json
import secrets
from functools import wraps
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils import timezone

from attendance.models import AttendanceRecord
from meals.models import MealPlan
from users.models import ActiveSession, PasswordResetToken, UserProfile


QR_EXPIRY_SECONDS = 30

MEAL_WINDOWS = [
    {'type': 'Breakfast', 'start': (7, 0), 'end': (9, 30)},
    {'type': 'Lunch', 'start': (12, 30), 'end': (14, 30)},
    {'type': 'Dinner', 'start': (19, 30), 'end': (21, 30)},
]


def json_error(message, status=400, **extra):
    payload = {'detail': message}
    payload.update(extra)
    return JsonResponse(payload, status=status)


def json_success(**payload):
    payload.setdefault('success', True)
    return JsonResponse(payload)


def parse_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


def get_user_role(user):
    profile = getattr(user, 'profile', None)
    if profile:
        return profile.role
    return UserProfile.ROLE_USER


def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def get_or_create_meal_plan(user):
    meal_plan, _ = MealPlan.objects.get_or_create(user=user)
    return meal_plan


def meal_plan_summary(meal_plan):
    items = []
    if meal_plan.breakfast:
        items.append('B')
    if meal_plan.lunch:
        items.append('L')
    if meal_plan.dinner:
        items.append('D')
    return '/'.join(items) if items else 'None'


def serialize_meal_plan(meal_plan):
    return {
        'breakfast': meal_plan.breakfast,
        'lunch': meal_plan.lunch,
        'dinner': meal_plan.dinner,
        'daysRemaining': meal_plan.days_remaining,
        'totalDays': meal_plan.total_days,
        'validUntil': meal_plan.valid_until.isoformat() if meal_plan.valid_until else None,
    }


def serialize_user(user, include_meal_plan=False):
    profile = get_or_create_profile(user)
    meal_plan = get_or_create_meal_plan(user)

    data = {
        'id': user.id,
        'name': user.get_full_name() or user.username,
        'email': user.email,
        'phone': profile.phone,
        'registrationNumber': profile.registration_number,
        'sourceId': profile.source_id,
        'role': profile.role,
        'status': profile.status,
        'plan': meal_plan_summary(meal_plan),
    }

    if include_meal_plan:
        data['mealPlan'] = serialize_meal_plan(meal_plan)

    return data


def format_attendance(record):
    return {
        'id': record.id,
        'userId': record.user_id,
        'userName': record.user_name_snapshot,
        'date': record.date.isoformat(),
        'time': record.time.strftime('%H:%M'),
        'type': record.meal_type,
        'status': record.status,
    }


def get_current_meal_window(now=None):
    now = now or timezone.localtime()
    current_minutes = now.hour * 60 + now.minute

    for window in MEAL_WINDOWS:
        start_minutes = window['start'][0] * 60 + window['start'][1]
        end_minutes = window['end'][0] * 60 + window['end'][1]
        if start_minutes <= current_minutes < end_minutes:
            return {
                'type': window['type'],
                'start': f"{window['start'][0]:02d}:{window['start'][1]:02d}",
                'end': f"{window['end'][0]:02d}:{window['end'][1]:02d}",
            }

    return None


def normalize_meal_type(value):
    if not value:
        return None
    normalized = str(value).strip().lower()
    if normalized == 'breakfast':
        return 'Breakfast'
    if normalized == 'lunch':
        return 'Lunch'
    if normalized == 'dinner':
        return 'Dinner'
    return None


def sign_qr_payload(user_id, meal_type, timestamp):
    message = f'{user_id}|{meal_type}|{timestamp}'
    return hmac.new(settings.SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()


def build_qr_payload(user, meal_type, timestamp=None):
    timestamp = int(timestamp or timezone.now().timestamp() * 1000)
    meal_type = normalize_meal_type(meal_type) or 'Lunch'
    payload = {
        'userId': str(user.id),
        'userName': user.get_full_name() or user.username,
        'mealType': meal_type,
        'timestamp': timestamp,
    }
    payload['signature'] = sign_qr_payload(payload['userId'], payload['mealType'], payload['timestamp'])
    return payload


def parse_scanned_payload(raw_payload):
    if isinstance(raw_payload, dict):
        return raw_payload
    if not raw_payload:
        raise ValueError('Invalid QR code format')
    try:
        return json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise ValueError('Invalid QR code format') from exc


def verify_qr_payload(raw_payload):
    payload = parse_scanned_payload(raw_payload)

    user_id = str(payload.get('userId') or payload.get('user_id') or '').strip()
    meal_type = normalize_meal_type(payload.get('mealType') or payload.get('meal_type'))
    timestamp = payload.get('timestamp')
    signature = payload.get('signature')

    if not user_id or not meal_type or timestamp is None or not signature:
        raise ValueError('QR payload is missing required fields')

    try:
        timestamp = int(timestamp)
    except (TypeError, ValueError) as exc:
        raise ValueError('QR payload timestamp is invalid') from exc

    expected_signature = sign_qr_payload(user_id, meal_type, timestamp)
    if not hmac.compare_digest(expected_signature, str(signature)):
        raise ValueError('QR signature is invalid')

    age_ms = int(timezone.now().timestamp() * 1000) - timestamp
    if age_ms < 0 or age_ms > QR_EXPIRY_SECONDS * 1000:
        raise ValueError('QR code has expired')

    active_window = get_current_meal_window()
    if not active_window:
        raise ValueError('No meal session is active right now')

    if active_window['type'] != meal_type:
        raise ValueError(f'This QR is for {meal_type}, not {active_window["type"]}')

    user_model = get_user_model()
    try:
        user = user_model.objects.get(pk=user_id)
    except user_model.DoesNotExist as exc:
        raise ValueError('User not found') from exc

    return {
        'user': user,
        'payload': payload,
        'meal_type': meal_type,
    }


def authenticate_request(request):
    authorization = request.headers.get('Authorization', '')
    if not authorization.startswith('Bearer '):
        return None, None

    token = authorization.split(' ', 1)[1].strip()
    try:
        session = ActiveSession.objects.select_related('user', 'user__profile').get(
            token=token,
            is_active=True,
        )
    except ActiveSession.DoesNotExist:
        return None, None

    session.last_seen = timezone.now()
    session.save(update_fields=['last_seen'])
    return session.user, session


def require_auth(roles=None):
    roles = set(roles or [])

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user, session = authenticate_request(request)
            if not user:
                return json_error('Authentication required', status=401)

            if roles and get_user_role(user) not in roles:
                return json_error('You do not have permission to access this resource', status=403)

            request.api_user = user
            request.api_session = session
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def create_password_reset_token(user):
    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(hours=1)
    return PasswordResetToken.objects.create(user=user, token=token, expires_at=expires_at)
