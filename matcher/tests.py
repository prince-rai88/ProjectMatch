from django.contrib.auth import get_user_model
from django.test import TestCase

from .matching import find_top_matches
from .models import Profile

User = get_user_model()


class GapAwareMatchingTests(TestCase):
    def setUp(self):
        # Create Target User
        self.user_target = User.objects.create_user(username="target", password="testpassword")
        self.profile_target = Profile.objects.create(
            user=self.user_target,
            skills="Python, Django, AI",
            interests="Fintech, Web apps",
            looking_for="Looking for teammates with design and development experience.",
        )

        # Create Profile A (Developer match)
        self.user_a = User.objects.create_user(username="dev_user", password="testpassword")
        self.profile_a = Profile.objects.create(
            user=self.user_a,
            skills="Python, javascript, Docker, backend",
            interests="Fintech",
            looking_for="Looking for a backend team.",
        )

        # Create Profile B (Designer match)
        self.user_b = User.objects.create_user(username="designer_user", password="testpassword")
        self.profile_b = Profile.objects.create(
            user=self.user_b,
            skills="Figma, UI design, UX, Graphic Design",
            interests="Product design",
            looking_for="Looking for creative opportunities.",
        )

    def test_default_matching_without_gap(self):
        # Profile A has overlapping skills/interests (Python, Fintech) with Target
        # Profile B has design skills
        matches = find_top_matches(self.profile_target, missing_role=None)
        
        # Verify both match results are present
        self.assertTrue(len(matches) > 0)
        # We check that matches are returned and sorted by score
        self.assertTrue(matches[0].score >= matches[1].score if len(matches) > 1 else True)

    def test_gap_aware_boosting_designer(self):
        # Boost for Designer gap: Profile B should be promoted
        matches = find_top_matches(self.profile_target, missing_role="Designer")
        
        self.assertTrue(len(matches) > 0)
        # Profile B should be first due to Designer boosting (+0.25)
        self.assertEqual(matches[0].profile.user.username, "designer_user")
        self.assertTrue(matches[0].is_gap_fit)
        self.assertIn("Fills your Designer gap", matches[0].explanation)
        self.assertIn("Figma", matches[0].explanation)
        self.assertIn("UI design", matches[0].explanation)

    def test_gap_aware_boosting_developer(self):
        # Boost for Developer gap: Profile A should still be first and flagged
        matches = find_top_matches(self.profile_target, missing_role="Developer")
        
        self.assertTrue(len(matches) > 0)
        self.assertEqual(matches[0].profile.user.username, "dev_user")
        self.assertTrue(matches[0].is_gap_fit)
        self.assertIn("Fills your Developer gap", matches[0].explanation)
        self.assertIn("Python", matches[0].explanation)

    def test_matching_fetches_candidates_in_one_joined_query(self):
        """Candidate user data is joined up front, avoiding an N+1 query pattern."""
        with self.assertNumQueries(1):
            matches = find_top_matches(self.profile_target)
            for match in matches:
                match.profile.user.username


class SignUpFlowTests(TestCase):
    def test_signup_authenticates_with_the_configured_backend(self):
        response = self.client.post(
            "/signup/",
            {
                "username": "new_member",
                "password1": "ReliablePass123!",
                "password2": "ReliablePass123!",
            },
        )

        self.assertRedirects(response, "/profile/", fetch_redirect_response=False)
        self.assertIn("_auth_user_id", self.client.session)
