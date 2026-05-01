# users/utils.py
import secrets
import string
from django.contrib.auth.models import User
from .models import School, SchoolUser

def create_school_account(school):
    username = school.census_number

    # generate a random 8-character password
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(8))

    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, password=password)
        SchoolUser.objects.create(user=user, school=school)
        print(f"✅ Created account for {school.name} — Password: {password}")
        return password
    else:
        print(f"⚠️ Account already exists for {school.name}")
        return None


def get_user_role(user):
    """Returns the user's role string or None if they are a school user."""
    if hasattr(user, 'profile'):
        return user.profile.role
    return None

def is_provincial(user):
    return get_user_role(user) == 'provincial'

def is_zonal(user):
    return get_user_role(user) == 'zonal'

def is_divisional(user):
    return get_user_role(user) == 'divisional'

def can_assign_projects(user):
    """Only provincial and zonal directors can assign projects."""
    return get_user_role(user) in ('provincial', 'zonal')

def get_user_zone(user):
    """Returns the Zone for a zonal director, or None for provincial."""
    if hasattr(user, 'profile') and user.profile.zone:
        return user.profile.zone
    return None
