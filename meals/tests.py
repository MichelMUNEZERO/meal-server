import json

from django.contrib.auth.models import User
from django.test import Client, TestCase

from meal_system.api_utils import get_or_create_meal_plan
from users.models import ActiveSession, UserProfile


class MealPlanAccessTests(TestCase):
	def setUp(self):
		self.client = Client()

		self.admin = User.objects.create_user(username='admin@example.com', email='admin@example.com', password='password123')
		UserProfile.objects.create(user=self.admin, role=UserProfile.ROLE_ADMIN, status=UserProfile.STATUS_ACTIVE)
		self.admin_session = ActiveSession.objects.create(user=self.admin, token='admin-token', is_active=True)

		self.member = User.objects.create_user(username='member@example.com', email='member@example.com', password='password123')
		UserProfile.objects.create(user=self.member, role=UserProfile.ROLE_USER, status=UserProfile.STATUS_ACTIVE)
		self.member_session = ActiveSession.objects.create(user=self.member, token='member-token', is_active=True)

		self.other_member = User.objects.create_user(username='other@example.com', email='other@example.com', password='password123')
		UserProfile.objects.create(user=self.other_member, role=UserProfile.ROLE_USER, status=UserProfile.STATUS_ACTIVE)

		plan = get_or_create_meal_plan(self.member)
		plan.breakfast = True
		plan.lunch = True
		plan.dinner = False
		plan.save()

	def test_normal_user_can_view_own_meal_plan(self):
		response = self.client.get(
			f'/api/users/{self.member.id}/meal-plan/',
			HTTP_AUTHORIZATION=f'Bearer {self.member_session.token}',
		)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json()['breakfast'])

	def test_normal_user_cannot_view_other_user_meal_plan(self):
		response = self.client.get(
			f'/api/users/{self.other_member.id}/meal-plan/',
			HTTP_AUTHORIZATION=f'Bearer {self.member_session.token}',
		)
		self.assertEqual(response.status_code, 403)

	def test_normal_user_cannot_update_own_meal_plan(self):
		response = self.client.patch(
			f'/api/users/{self.member.id}/meal-plan/',
			data=json.dumps({'dinner': True}),
			content_type='application/json',
			HTTP_AUTHORIZATION=f'Bearer {self.member_session.token}',
		)
		self.assertEqual(response.status_code, 403)

	def test_admin_can_update_meal_plan(self):
		response = self.client.patch(
			f'/api/users/{self.member.id}/meal-plan/',
			data=json.dumps({'dinner': True}),
			content_type='application/json',
			HTTP_AUTHORIZATION=f'Bearer {self.admin_session.token}',
		)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json()['dinner'])
