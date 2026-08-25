from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm, ProfileForm
from .matching import find_top_matches
from .models import Profile


def home(request):
    if request.user.is_authenticated:
        return redirect("profile_edit")
    return render(request, "home.html")


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("profile_edit")

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return redirect(self.get_success_url())



@login_required
def profile_edit(request):
    profile, _created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile_edit")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "matcher/profile_form.html", {"form": form})


@login_required
def find_matches(request):
    profile, _created = Profile.objects.get_or_create(user=request.user)
    missing_role = request.GET.get("missing_role", "").strip()
    
    roles_list = [
        "Designer",
        "Developer",
        "Domain Expert",
        "Data/Research",
        "Marketing/Ops"
    ]
    
    # Validate the selected missing role
    if missing_role not in roles_list:
        missing_role = None
        
    matches = find_top_matches(profile, missing_role=missing_role)
    
    return render(
        request,
        "matcher/matches.html",
        {
            "profile": profile,
            "matches": matches,
            "roles": roles_list,
            "selected_role": missing_role
        },
    )

