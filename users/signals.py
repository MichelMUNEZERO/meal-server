from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from datetime import datetime, timedelta
from django.utils import timezone

from attendance.models import AttendanceRecord
from meals.models import MealPlan
from users.models import UserProfile


def upsert_user(*, username, email, password, first_name, last_name, role, status='Active', is_staff=False, is_superuser=False):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'is_staff': is_staff,
            'is_superuser': is_superuser,
        },
    )

    changed = False
    if user.email != email:
        user.email = email
        changed = True
    if user.first_name != first_name:
        user.first_name = first_name
        changed = True
    if user.last_name != last_name:
        user.last_name = last_name
        changed = True
    if user.is_staff != is_staff:
        user.is_staff = is_staff
        changed = True
    if user.is_superuser != is_superuser:
        user.is_superuser = is_superuser
        changed = True
    if created or not user.check_password(password):
        user.set_password(password)
        changed = True
    if changed:
        user.save()

    profile, _ = UserProfile.objects.get_or_create(user=user)
    if profile.role != role:
        profile.role = role
        changed = True
    if profile.status != status:
        profile.status = status
        changed = True
    if changed:
        profile.save()

    return user


@receiver(post_migrate)
def seed_demo_data(sender, **kwargs):
    app_config = kwargs.get('app_config')
    if not app_config or app_config.label != 'users':
        return

    member = upsert_user(
        username='michel@example.com',
        email='michel@example.com',
        password='password',
        first_name='Michel',
        last_name='Munezero',
        role=UserProfile.ROLE_USER,
    )
    admin = upsert_user(
        username='admin@trackers.com',
        email='admin@trackers.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        role=UserProfile.ROLE_ADMIN,
        is_staff=True,
        is_superuser=True,
    )
    scanner = upsert_user(
        username='scanner@trackers.com',
        email='scanner@trackers.com',
        password='scanner123',
        first_name='Scanner',
        last_name='Agent',
        role=UserProfile.ROLE_SCANNER,
    )
    john = upsert_user(
        username='john@example.com',
        email='john@example.com',
        password='password',
        first_name='John',
        last_name='Doe',
        role=UserProfile.ROLE_USER,
    )
    jane = upsert_user(
        username='jane@example.com',
        email='jane@example.com',
        password='password',
        first_name='Jane',
        last_name='Smith',
        role=UserProfile.ROLE_USER,
        status=UserProfile.STATUS_INACTIVE,
    )

    meal_plans = {
        member.id: dict(breakfast=True, lunch=True, dinner=False, days_remaining=15, total_days=30, valid_until=datetime(2026, 5, 30).date()),
        admin.id: dict(breakfast=False, lunch=False, dinner=False, days_remaining=0, total_days=30, valid_until=None),
        scanner.id: dict(breakfast=False, lunch=False, dinner=False, days_remaining=0, total_days=30, valid_until=None),
        john.id: dict(breakfast=True, lunch=True, dinner=True, days_remaining=22, total_days=30, valid_until=datetime(2026, 6, 15).date()),
        jane.id: dict(breakfast=False, lunch=False, dinner=False, days_remaining=0, total_days=30, valid_until=None),
    }

    for user_id, plan_data in meal_plans.items():
        MealPlan.objects.update_or_create(user_id=user_id, defaults=plan_data)

    if not AttendanceRecord.objects.exists():
        AttendanceRecord.objects.create(
            user=member,
            user_name_snapshot='Michel Munezero',
            meal_type=AttendanceRecord.BREAKFAST,
            date=timezone.localdate() - timedelta(days=1),
            time=datetime.strptime('08:15', '%H:%M').time(),
            status=AttendanceRecord.STATUS_PRESENT,
            payload={},
        )
        AttendanceRecord.objects.create(
            user=member,
            user_name_snapshot='Michel Munezero',
            meal_type=AttendanceRecord.LUNCH,
            date=timezone.localdate() - timedelta(days=1),
            time=datetime.strptime('13:05', '%H:%M').time(),
            status=AttendanceRecord.STATUS_PRESENT,
            payload={},
        )
        AttendanceRecord.objects.create(
            user=john,
            user_name_snapshot='John Doe',
            meal_type=AttendanceRecord.LUNCH,
            date=timezone.localdate(),
            time=datetime.strptime('13:15', '%H:%M').time(),
            status=AttendanceRecord.STATUS_PRESENT,
            payload={},
        )
