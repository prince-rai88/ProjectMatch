"""Manual sign-up then login smoke test; safe to import during test discovery."""

import os

import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectmatch.settings")
    django.setup()
    from django.contrib.auth.models import User
    from django.test import Client

    User.objects.filter(username="signup_test_user").delete()
    client = Client()
    signup_response = client.post(
        "/signup/",
        {"username": "signup_test_user", "password1": "StrongPass123!", "password2": "StrongPass123!"},
    )
    print("Signup status:", signup_response.status_code)
    if signup_response.status_code != 302:
        print("Signup errors:", signup_response.context["form"].errors)

    client.logout()
    login_response = client.post("/login/", {"username": "signup_test_user", "password": "StrongPass123!"})
    print("Login status:", login_response.status_code)
    if login_response.status_code != 302:
        print("Login errors:", login_response.context["form"].errors)


if __name__ == "__main__":
    main()
