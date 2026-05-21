from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from attendance.models import AttendanceRecord
from meal_system.api_utils import (
	build_qr_payload,
	format_attendance,
	get_or_create_meal_plan,
	json_error,
	json_success,
	parse_json_body,
	require_auth,
	serialize_meal_plan,
	verify_qr_payload,
)
from users.models import UserProfile


User = get_user_model()


@csrf_exempt
@require_auth(roles=[UserProfile.ROLE_ADMIN])
def attendance_list(request):
	if request.method != 'GET':
		return json_error('Method not allowed', status=405)

	queryset = AttendanceRecord.objects.select_related('user').all()
	user_id = request.GET.get('user')
	if user_id:
		queryset = queryset.filter(user_id=user_id)

	return JsonResponse([format_attendance(record) for record in queryset], safe=False)


@csrf_exempt
@require_auth(roles=[UserProfile.ROLE_ADMIN, UserProfile.ROLE_SCANNER])
def scanner_summary(request):
	if request.method != 'GET':
		return json_error('Method not allowed', status=405)

	limit = request.GET.get('limit', '5')
	try:
		limit = int(limit)
	except (TypeError, ValueError):
		limit = 5
	limit = max(1, min(limit, 10))

	today = timezone.localdate()
	total_today = AttendanceRecord.objects.filter(date=today).count()
	recent_records = AttendanceRecord.objects.select_related('user').order_by('-created_at')[:limit]

	recent = [
		{
			'id': record.id,
			'userId': record.user_id,
			'userName': record.user_name_snapshot,
			'mealType': record.meal_type,
			'date': record.date.isoformat(),
			'time': record.time.strftime('%H:%M:%S'),
			'status': record.status,
		}
		for record in recent_records
	]

	return json_success(totalScannedToday=total_today, recentScans=recent)


@csrf_exempt
@require_auth(roles=[UserProfile.ROLE_ADMIN, UserProfile.ROLE_USER])
def generate_qr(request):
	if request.method != 'POST':
		return json_error('Method not allowed', status=405)

	data = parse_json_body(request)
	user_id = data.get('user_id') or data.get('userId') or request.api_user.id
	meal_type = data.get('meal_type') or data.get('mealType')

	user = User.objects.filter(pk=user_id).first()
	if not user:
		return json_error('User not found', status=404)

	try:
		payload = build_qr_payload(user, meal_type)
	except ValueError as exc:
		return json_error(str(exc), status=400)
	return JsonResponse(payload)


@csrf_exempt
@require_auth(roles=[UserProfile.ROLE_ADMIN, UserProfile.ROLE_SCANNER])
def verify_scan(request):
	if request.method != 'POST':
		return json_error('Method not allowed', status=405)

	data = parse_json_body(request)
	raw_payload = data.get('payload')

	try:
		verified = verify_qr_payload(raw_payload)
	except ValueError as exc:
		return json_error(str(exc), status=400)

	user = verified['user']
	payload = verified['payload']
	meal_type = verified['meal_type']
	today = timezone.localdate()
	now = timezone.localtime()

	try:
		record, created = AttendanceRecord.objects.get_or_create(
			user=user,
			date=today,
			meal_type=meal_type,
			defaults={
				'user_name_snapshot': user.get_full_name() or user.username,
				'time': now.time().replace(microsecond=0),
				'status': AttendanceRecord.STATUS_PRESENT,
				'payload': payload,
			},
		)
	except IntegrityError:
		return json_error('This user already checked in for this meal today', status=400)

	if not created:
		return json_error('This user already checked in for this meal today', status=400)

	meal_plan = get_or_create_meal_plan(user)

	return json_success(
		user={'id': user.id, 'name': user.get_full_name() or user.username},
		mealType=meal_type,
		mealPlan=serialize_meal_plan(meal_plan),
		record=format_attendance(record),
	)
