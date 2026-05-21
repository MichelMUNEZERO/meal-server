from django.contrib.auth.models import User
from django.db import models


class MealPlan(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='meal_plan')
	breakfast = models.BooleanField(default=False)
	lunch = models.BooleanField(default=False)
	dinner = models.BooleanField(default=False)
	days_remaining = models.PositiveIntegerField(default=0)
	total_days = models.PositiveIntegerField(default=30)
	valid_until = models.DateField(null=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f'{self.user.username} meal plan'
