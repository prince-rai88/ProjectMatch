from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Profile


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-input"})


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-input"})


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "skills",
            "interests",
            "availability",
            "experience_level",
            "looking_for",
        ]
        widgets = {
            # Skills and interests are hidden — replaced by Alpine.js tag inputs in the template
            "skills": forms.TextInput(attrs={"class": "hidden", "id": "id_skills"}),
            "interests": forms.TextInput(attrs={"class": "hidden", "id": "id_interests"}),
            "availability": forms.Select(attrs={"class": "form-input"}),
            "experience_level": forms.Select(attrs={"class": "form-input"}),
            "looking_for": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 4,
                "placeholder": "Describe the project, the role you need, or what a great collaborator looks like to you...",
                "style": "font-family:'JetBrains Mono',monospace;font-size:0.8125rem;resize:vertical;"
            }),
        }
