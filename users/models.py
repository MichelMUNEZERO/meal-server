from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
	ROLE_USER = 'user'
	ROLE_ADMIN = 'admin'
	ROLE_SCANNER = 'scanner'

	STATUS_ACTIVE = 'Active'
	STATUS_INACTIVE = 'Inactive'

	ROLE_CHOICES = [
		(ROLE_USER, 'Member'),
		(ROLE_ADMIN, 'Admin'),
		(ROLE_SCANNER, 'Scanner'),
	]

	STATUS_CHOICES = [
		(STATUS_ACTIVE, 'Active'),
		(STATUS_INACTIVE, 'Inactive'),
	]

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
	phone = models.CharField(max_length=32, blank=True, default='')
	source_id = models.PositiveIntegerField(null=True, blank=True, unique=True, db_index=True)
	registration_number = models.CharField(max_length=64, null=True, blank=True, unique=True, db_index=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.user.username} profile'


class ActiveSession(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='active_sessions')
	token = models.CharField(max_length=128, unique=True, db_index=True)
	session_id = models.CharField(max_length=128, blank=True, default='')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-last_seen']

	def __str__(self):
		return f'{self.user.username} session'


class PasswordResetToken(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
	token = models.CharField(max_length=128, unique=True, db_index=True)
	expires_at = models.DateTimeField()
	used_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.user.username} reset token'
