from functools import wraps
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render
from common.errors import AppError


def role_for(user):
    if not user.is_authenticated or not user.is_active:
        return None
    roles = list(user.groups.filter(name__in=["Student", "Organizer"]).values_list("name", flat=True))
    if len(roles) != 1:
        return None
    if roles[0] == "Student" and not hasattr(user, "student_profile"):
        return None
    return roles[0]


def require_role(user, roles):
    if not user.is_authenticated or not user.is_active:
        raise AppError("Please sign in to continue.", 401, "authentication_required")
    if role_for(user) not in roles:
        raise AppError("Your account does not have permission for this action.", 403, "permission_denied")


def page_access(*roles):
    def decorate(fn):
        @wraps(fn)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if role_for(request.user) not in roles:
                return render(request, "error.html", {"title": "Access restricted", "message": "This page is not available for your account role."}, status=403)
            return fn(request, *args, **kwargs)
        return wrapped
    return decorate
