from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import EmployeeCommissionForm, UserRegistrationForm, UserProfileForm
from .permissions import role_required


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
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def employees_list(request):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    employees = User.objects.all().order_by("role", "last_name", "first_name", "username")
    can_edit = getattr(request.user, "role", None) == "MANAGER"
    return render(
        request,
        "accounts/employees_list.html",
        {"employees": employees, "can_edit": can_edit},
    )


@role_required("MANAGER")
def employee_commission_edit(request, user_id: int):
    from django.contrib.auth import get_user_model
    from django.shortcuts import get_object_or_404

    User = get_user_model()
    employee = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        form = EmployeeCommissionForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {employee.get_full_name()}.")
            return redirect("employees_list")
    else:
        form = EmployeeCommissionForm(instance=employee)

    return render(request, "accounts/employee_edit.html", {"employee": employee, "form": form})

