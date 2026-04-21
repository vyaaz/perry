from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


def role_required(*roles: str):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user_role = getattr(request.user, "role", None)
            if user_role in roles:
                return view_func(request, *args, **kwargs)
            # Treat BOTH as satisfying SELLER and CLEANER checks.
            if user_role == "BOTH" and ("SELLER" in roles or "CLEANER" in roles):
                return view_func(request, *args, **kwargs)
            return redirect("dashboard")

        return _wrapped

    return decorator

