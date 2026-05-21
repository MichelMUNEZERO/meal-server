from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from meal_system.api_utils import (
	get_or_create_meal_plan,
	json_error,
	json_success,
	parse_json_body,
	require_auth,
	serialize_meal_plan,
)
from users.models import UserProfile


User = get_user_model()


@csrf_exempt
@require_auth(roles=[UserProfile.ROLE_ADMIN, UserProfile.ROLE_USER])
def user_meal_plan(request, user_id):
	user = User.objects.filter(pk=user_id).first()
	if not user:
		return json_error('User not found', status=404)

	requester_profile = getattr(request.api_user, 'profile', None)
	requester_role = requester_profile.role if requester_profile else UserProfile.ROLE_USER
	if requester_role == UserProfile.ROLE_USER and request.api_user.id != user.id:
		return json_error('You do not have permission to access this resource', status=403)

	meal_plan = get_or_create_meal_plan(user)

	if request.method == 'GET':
		return json_success(**serialize_meal_plan(meal_plan))

	if request.method in {'PUT', 'PATCH'}:
		if requester_role != UserProfile.ROLE_ADMIN:
			return json_error('You do not have permission to access this resource', status=403)
		data = parse_json_body(request)
		if 'breakfast' in data:
			meal_plan.breakfast = bool(data.get('breakfast'))
		if 'lunch' in data:
			meal_plan.lunch = bool(data.get('lunch'))
		if 'dinner' in data:
			meal_plan.dinner = bool(data.get('dinner'))
		if 'daysRemaining' in data:
			meal_plan.days_remaining = max(0, int(data.get('daysRemaining') or 0))
		if 'totalDays' in data:
			meal_plan.total_days = max(0, int(data.get('totalDays') or 0))
		if 'validUntil' in data:
			valid_until = data.get('validUntil')
			if valid_until:
				meal_plan.valid_until = datetime.fromisoformat(str(valid_until)).date()
			else:
				meal_plan.valid_until = None

		meal_plan.save()
		return json_success(**serialize_meal_plan(meal_plan))

	return json_error('Method not allowed', status=405)


@csrf_exempt
@require_auth(roles=[UserProfile.ROLE_ADMIN])
def all_meal_plans(request):
	if request.method != 'GET':
		return json_error('Method not allowed', status=405)

	plans = {}
	for user in User.objects.select_related('meal_plan').order_by('id'):
		meal_plan = get_or_create_meal_plan(user)
		plans[str(user.id)] = serialize_meal_plan(meal_plan)
	return JsonResponse(plans)
