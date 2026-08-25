from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "availability",
        "experience_level",
        "created_at",
    )
    search_fields = ("user__username", "skills", "interests", "looking_for")
    list_filter = ("availability", "experience_level")
