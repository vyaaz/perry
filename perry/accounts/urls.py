from django.urls import path

from .views import (
    employee_commission_edit,
    employees_list,
    login_view,
    logout_view,
    profile_view,
    register_view,
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("employees/", employees_list, name="employees_list"),
    path("employees/<int:user_id>/", employee_commission_edit, name="employee_commission_edit"),
]

