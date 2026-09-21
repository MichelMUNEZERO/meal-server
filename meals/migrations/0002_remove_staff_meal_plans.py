from django.db import migrations


def remove_staff_meal_plans(apps, schema_editor):
    MealPlan = apps.get_model('meals', 'MealPlan')
    UserProfile = apps.get_model('users', 'UserProfile')
    staff_user_ids = UserProfile.objects.exclude(role='user').values_list('user_id', flat=True)
    MealPlan.objects.filter(user_id__in=staff_user_ids).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('meals', '0001_initial'),
        ('users', '0005_activesession_expires_at'),
    ]

    operations = [
        migrations.RunPython(remove_staff_meal_plans, migrations.RunPython.noop),
    ]
