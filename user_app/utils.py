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
