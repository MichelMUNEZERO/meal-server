from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile, ActiveSession
from meal_system.api_utils import get_or_create_profile, get_or_create_meal_plan
import secrets


class Command(BaseCommand):
	help = 'Create a new user interactively'

	def add_arguments(self, parser):
		parser.add_argument('email', type=str, help='User email address')
		parser.add_argument('name', type=str, help='User full name')
		parser.add_argument('--password', type=str, help='User password (will be prompted if not provided)')
		parser.add_argument('--phone', type=str, default='', help='User phone number')
		parser.add_argument('--reg-number', type=str, default='', help='Registration number')
		parser.add_argument('--role', type=str, default='user', choices=['user', 'scanner', 'admin'], help='User role')
		parser.add_argument('--status', type=str, default='Active', choices=['Active', 'Inactive'], help='User status')
		parser.add_argument('--generate-password', action='store_true', help='Generate a random password')

	def handle(self, *args, **options):
		email = options['email'].strip().lower()
		name = options['name'].strip()
		phone = options['phone'].strip()
		reg_number = options['reg_number'].strip()
		role = options['role']
		status = options['status']

		if User.objects.filter(email__iexact=email).exists():
			self.stdout.write(self.style.ERROR(f'User with email {email} already exists'))
			return

		if reg_number and UserProfile.objects.filter(registration_number=reg_number).exists():
			self.stdout.write(self.style.ERROR(f'Registration number {reg_number} already exists'))
			return

		password = options['password']
		if options['generate_password']:
			password = secrets.token_urlsafe(10)
			self.stdout.write(self.style.SUCCESS(f'Generated password: {password}'))
		elif not password:
			import getpass
			password = getpass.getpass('Enter password: ')

		if len(password) < 8:
			self.stdout.write(self.style.ERROR('Password must be at least 8 characters'))
			return

		first_name, last_name = (name.split(' ', 1) + [''])[:2]
		user = User.objects.create_user(
			username=email,
			email=email,
			password=password,
			first_name=first_name,
			last_name=last_name,
			is_active=status == 'Active',
		)

		profile = get_or_create_profile(user)
		profile.role = role
		profile.status = status
		profile.phone = phone
		if reg_number:
			profile.registration_number = reg_number
		profile.save()

		meal_plan = get_or_create_meal_plan(user)
		meal_plan.save()

		self.stdout.write(self.style.SUCCESS(f'User {email} created successfully'))
		self.stdout.write(f'Name: {name}')
		self.stdout.write(f'Role: {role}')
		self.stdout.write(f'Status: {status}')
