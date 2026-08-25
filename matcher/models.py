from django.conf import settings
from django.db import models


class Profile(models.Model):
    class Availability(models.TextChoices):
        WEEKENDS = "weekends", "Weekends"
        EVENINGS = "evenings", "Evenings"
        FULL_TIME = "full_time", "Full-time"
        FLEXIBLE = "flexible", "Flexible"

    class ExperienceLevel(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    skills = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated skills, e.g. Python, UI design, Django",
    )
    interests = models.CharField(max_length=255, blank=True)
    availability = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.FLEXIBLE,
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.BEGINNER,
    )
    looking_for = models.TextField(
        blank=True,
        help_text="Describe the project, teammates, or role you want. Used later for AI matching.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
