from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('users', '0003_userprofile_is_temporary_password_and_more'),
	]

	operations = [
		migrations.AddField(
			model_name='userprofile',
			name='year_of_study',
			field=models.CharField(blank=True, default='', max_length=32),
		),
		migrations.AddField(
			model_name='userprofile',
			name='event_name',
			field=models.CharField(blank=True, default='', max_length=255),
		),
	]