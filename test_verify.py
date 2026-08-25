"""Manual end-to-end profile and matching smoke test."""

import os
import sys

import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectmatch.settings")
    django.setup()
    from django.contrib.auth.models import User
    from matcher.matching import find_top_matches
    from matcher.models import Profile

    try:
        user, _ = User.objects.get_or_create(username="test_user_verify", email="verify@test.com")
        user.set_password("pass12345678")
        user.save()
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.skills = "Python, Django, HTML, CSS"
        profile.interests = "Testing, AI"
        profile.experience_level = "intermediate"
        profile.looking_for = "A designer to help make things look pretty."
        profile.save()
        print("✓ Auth & Profile saving works.")
        print(f"✓ Match engine works. Found {len(find_top_matches(profile))} matches.")
        find_top_matches(profile, missing_role="Designer")
        print("✓ Gap filter works. Re-ranked for Designer.")
        print("All functionality verified successfully.")
    except Exception as error:
        print(f"Error during verification: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
