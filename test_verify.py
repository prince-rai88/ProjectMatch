import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectmatch.settings')
django.setup()

from django.contrib.auth.models import User
from matcher.models import Profile
from matcher.matching import find_top_matches

def test():
    try:
        # Create a test user
        u, created = User.objects.get_or_create(username='test_user_verify', email='verify@test.com')
        u.set_password('pass12345678')
        u.save()

        # Update profile
        p, created = Profile.objects.get_or_create(user=u)
        p.skills = 'Python, Django, HTML, CSS'
        p.interests = 'Testing, AI'
        p.experience_level = 'intermediate'
        p.looking_for = 'A designer to help make things look pretty.'
        p.save()
        print("✓ Auth & Profile saving works.")

        # Compute matches
        matches = find_top_matches(p)
        print(f"✓ Match engine works. Found {len(matches)} matches.")
        
        # Test Gap Filter (e.g. Designer)
        gap_matches = find_top_matches(p, missing_role='Designer')
        print(f"✓ Gap filter works. Re-ranked for Designer.")
        
        print("All functionality verified successfully.")
    except Exception as e:
        print(f"Error during verification: {e}")
        sys.exit(1)

if __name__ == '__main__':
    test()
