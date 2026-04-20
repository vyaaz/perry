from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import UserRegistrationForm, UserProfileForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next") or "dashboard")
        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


def register_view(request):
    """User registration with role selection"""
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    
    return render(request, "accounts/register.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def profile_view(request):
    """User profile page"""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, "accounts/profile.html", {"form": form})

