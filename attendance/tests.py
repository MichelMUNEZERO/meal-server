from datetime import datetime, time, timezone as dt_timezone

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from attendance.models import AttendanceRecord
from meal_system.api_utils import get_current_meal_window
from users.models import ActiveSession, UserProfile


class AttendanceAccessTests(TestCase):
	def setUp(self):
		self.client = Client()

		self.admin = User.objects.create_user(username='admin@example.com', email='admin@example.com', password='password123')
		UserProfile.objects.create(user=self.admin, role=UserProfile.ROLE_ADMIN, status=UserProfile.STATUS_ACTIVE)
		self.admin_session = ActiveSession.objects.create(user=self.admin, token='admin-token', is_active=True)

		self.scanner = User.objects.create_user(username='scanner@example.com', email='scanner@example.com', password='password123')
		UserProfile.objects.create(user=self.scanner, role=UserProfile.ROLE_SCANNER, status=UserProfile.STATUS_ACTIVE)
		self.scanner_session = ActiveSession.objects.create(user=self.scanner, token='scanner-token', is_active=True)

		self.member = User.objects.create_user(username='member@example.com', email='member@example.com', password='password123')
		UserProfile.objects.create(user=self.member, role=UserProfile.ROLE_USER, status=UserProfile.STATUS_ACTIVE)
		self.member_session = ActiveSession.objects.create(user=self.member, token='member-token', is_active=True)

		meal_types = [AttendanceRecord.BREAKFAST, AttendanceRecord.LUNCH, AttendanceRecord.DINNER]
		for idx, meal_type in enumerate(meal_types):
			AttendanceRecord.objects.create(
				user=self.member,
				user_name_snapshot='Member User',
				meal_type=meal_type,
				date=timezone.localdate(),
				time=time(hour=12 + idx, minute=0),
				status=AttendanceRecord.STATUS_PRESENT,
				payload={'index': idx},
			)

	def test_scanner_can_get_summary(self):
		response = self.client.get(
			'/api/attendance/scanner-summary/?limit=2',
			HTTP_AUTHORIZATION=f'Bearer {self.scanner_session.token}',
		)

		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertGreaterEqual(payload['totalScannedToday'], 3)
		self.assertEqual(len(payload['recentScans']), 2)

	def test_scanner_cannot_access_attendance_list(self):
		response = self.client.get(
			'/api/attendance/',
			HTTP_AUTHORIZATION=f'Bearer {self.scanner_session.token}',
		)
		self.assertEqual(response.status_code, 403)

	def test_normal_user_cannot_access_attendance_list(self):
		response = self.client.get(
			'/api/attendance/',
			HTTP_AUTHORIZATION=f'Bearer {self.member_session.token}',
		)
		self.assertEqual(response.status_code, 403)

	def test_meal_windows_match_event_schedule(self):
		morning = timezone.make_aware(datetime(2026, 5, 21, 6, 30), dt_timezone.utc)
		midday = timezone.make_aware(datetime(2026, 5, 21, 13, 0), dt_timezone.utc)
		evening = timezone.make_aware(datetime(2026, 5, 21, 19, 0), dt_timezone.utc)

		self.assertEqual(get_current_meal_window(morning)['type'], 'Breakfast')
		self.assertEqual(get_current_meal_window(midday)['type'], 'Lunch')
		self.assertEqual(get_current_meal_window(evening)['type'], 'Dinner')
