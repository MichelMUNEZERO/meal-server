from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('users', '0004_userprofile_year_of_study_event_name'),
	]

	operations = [
		migrations.AddField(
			model_name='activesession',
			name='expires_at',
			field=models.DateTimeField(blank=True, null=True),
		),
	]