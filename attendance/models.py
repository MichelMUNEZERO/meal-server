from django.contrib.auth.models import User
from django.db import models


class AttendanceRecord(models.Model):
	BREAKFAST = 'Breakfast'
	LUNCH = 'Lunch'
	DINNER = 'Dinner'

	MEAL_CHOICES = [
		(BREAKFAST, 'Breakfast'),
		(LUNCH, 'Lunch'),
		(DINNER, 'Dinner'),
	]

	STATUS_PRESENT = 'Present'
	STATUS_DENIED = 'Denied'

	STATUS_CHOICES = [
		(STATUS_PRESENT, 'Present'),
		(STATUS_DENIED, 'Denied'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
	user_name_snapshot = models.CharField(max_length=255)
	meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)
	date = models.DateField(db_index=True)
	time = models.TimeField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PRESENT)
	payload = models.JSONField(default=dict, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-date', '-time', '-created_at']
		constraints = [
			models.UniqueConstraint(fields=['user', 'date', 'meal_type'], name='unique_user_meal_day')
		]

	def __str__(self):
		return f'{self.user_name_snapshot} - {self.meal_type} - {self.date}'
