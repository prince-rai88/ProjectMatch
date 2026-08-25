"""Manual sign-up form smoke test; safe to import during Django test discovery."""

import os

import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectmatch.settings")
    django.setup()
    from matcher.forms import CustomUserCreationForm

    form = CustomUserCreationForm(
        data={"username": "signupuser", "password1": "Password123!", "password2": "Password123!"}
    )
    print("Form bound:", form.is_bound)
    print("Form valid:", form.is_valid())
    if not form.is_valid():
        print("Form errors:", form.errors)


if __name__ == "__main__":
    main()
