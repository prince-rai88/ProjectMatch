"""Manual form and authentication smoke test; safe to import during discovery."""

import os

import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectmatch.settings")
    django.setup()
    from django.contrib.auth import authenticate
    from matcher.forms import CustomAuthenticationForm, CustomUserCreationForm

    signup_data = {"username": "newuser1", "password1": "TestingPass123!", "password2": "TestingPass123!"}
    form = CustomUserCreationForm(data=signup_data)
    if form.is_valid():
        user = form.save()
        print("User saved:", user.username)
        print("Password hashed:", user.password.startswith("pbkdf2_"))
    else:
        print("Signup invalid:", form.errors)

    auth_form = CustomAuthenticationForm(data={"username": "newuser1", "password": "TestingPass123!"})
    print("Auth form valid:", auth_form.is_valid())
    print("Direct authentication:", bool(authenticate(username="newuser1", password="TestingPass123!")))


if __name__ == "__main__":
    main()
