"""
Admin user management utilities for the Meal System.
Provides helper functions for managing users, roles, and permissions.
"""

from django.contrib.auth.models import User
from users.models import UserProfile, ActiveSession
from meal_system.api_utils import get_or_create_profile, get_or_create_meal_plan
from django.db import transaction


def create_admin_user(email, name, password, phone='', registration_number=''):
	"""Create a new admin user."""
	return create_user(
		email=email,
		name=name,
		password=password,
		phone=phone,
		registration_number=registration_number,
		role=UserProfile.ROLE_ADMIN,
	)


def create_scanner_user(email, name, password, phone='', registration_number=''):
	"""Create a new scanner user."""
	return create_user(
		email=email,
		name=name,
		password=password,
		phone=phone,
		registration_number=registration_number,
		role=UserProfile.ROLE_SCANNER,
	)


def create_user(email, name, password, phone='', registration_number='', role=UserProfile.ROLE_USER, status=UserProfile.STATUS_ACTIVE):
	"""
	Create a new user with the specified details.

	Args:
		email: User email address
		name: User full name
		password: User password (min 8 characters)
		phone: Optional phone number
		registration_number: Optional registration number
		role: User role (user, scanner, admin)
		status: User status (Active, Inactive)

	Returns:
		User object on success

	Raises:
		ValueError: If validation fails
	"""
	if not email or not name or not password:
		raise ValueError('Email, name, and password are required')

	if len(password) < 8:
		raise ValueError('Password must be at least 8 characters')

	if User.objects.filter(email__iexact=email).exists():
		raise ValueError(f'User with email {email} already exists')

	if registration_number and UserProfile.objects.filter(registration_number=registration_number).exists():
		raise ValueError(f'Registration number {registration_number} already exists')

	with transaction.atomic():
		first_name, last_name = (name.split(' ', 1) + [''])[:2]
		user = User.objects.create_user(
			username=email.lower(),
			email=email.lower(),
			password=password,
			first_name=first_name,
			last_name=last_name,
			is_active=status == UserProfile.STATUS_ACTIVE,
		)

		profile = get_or_create_profile(user)
		profile.role = role
		profile.status = status
		profile.phone = phone
		if registration_number:
			profile.registration_number = registration_number
		profile.save()

		meal_plan = get_or_create_meal_plan(user)
		meal_plan.save()

	return user


def update_user_role(user_id, new_role):
	"""
	Update a user's role.

	Args:
		user_id: User ID
		new_role: New role (user, scanner, admin)

	Returns:
		Updated UserProfile object

	Raises:
		User.DoesNotExist: If user not found
		ValueError: If invalid role
	"""
	if new_role not in dict(UserProfile.ROLE_CHOICES):
		raise ValueError(f'Invalid role: {new_role}')

	user = User.objects.get(pk=user_id)
	profile = get_or_create_profile(user)
	profile.role = new_role
	profile.save()
	return profile


def list_users_by_role(role):
	"""
	Get all users with a specific role.

	Args:
		role: Role to filter by (user, scanner, admin)

	Returns:
		QuerySet of users with the specified role
	"""
	if role not in dict(UserProfile.ROLE_CHOICES):
		raise ValueError(f'Invalid role: {role}')

	return User.objects.filter(profile__role=role).select_related('profile', 'meal_plan')


def deactivate_user(user_id):
	"""
	Deactivate a user account.

	Args:
		user_id: User ID

	Returns:
		Updated UserProfile object

	Raises:
		User.DoesNotExist: If user not found
	"""
	user = User.objects.get(pk=user_id)
	user.is_active = False
	user.save()

	profile = get_or_create_profile(user)
	profile.status = UserProfile.STATUS_INACTIVE
	profile.save()

	ActiveSession.objects.filter(user=user).update(is_active=False)
	return profile


def activate_user(user_id):
	"""
	Activate a user account.

	Args:
		user_id: User ID

	Returns:
		Updated UserProfile object

	Raises:
		User.DoesNotExist: If user not found
	"""
	user = User.objects.get(pk=user_id)
	user.is_active = True
	user.save()

	profile = get_or_create_profile(user)
	profile.status = UserProfile.STATUS_ACTIVE
	profile.save()

	return profile
