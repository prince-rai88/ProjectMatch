"""Manual login endpoint smoke test; safe to import during Django test discovery."""

import os

import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectmatch.settings")
    django.setup()
    from django.contrib.auth.models import User
    from django.test import Client

    User.objects.filter(username="test_login_bug").delete()
    User.objects.create_user("test_login_bug", "test@example.com", "Pass1234!")
    response = Client().post("/login/", {"username": "test_login_bug", "password": "Pass1234!"})
    print("Status code:", response.status_code)
    if response.status_code == 200:
        print("Form errors:", response.context["form"].errors)
    else:
        print("Redirected to:", response.url)


if __name__ == "__main__":
    main()
