"""Manual authentication smoke test; safe to import during Django test discovery."""

import os

import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectmatch.settings")
    django.setup()

    from django.contrib.auth import authenticate
    from django.contrib.auth.models import User
    from matcher.forms import CustomAuthenticationForm

    user, _ = User.objects.get_or_create(username="testloginuser")
    user.set_password("TestPass123!")
    user.save()
    print("User created:", user.username)
    print("Checking authenticate():", authenticate(username="testloginuser", password="TestPass123!"))
    form = CustomAuthenticationForm(data={"username": "testloginuser", "password": "TestPass123!"})
    print("Form is valid:", form.is_valid())
    if not form.is_valid():
        print("Form errors:", form.errors)


if __name__ == "__main__":
    main()
