from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """Redirect members to password change page until they choose a new password."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated and getattr(user, "must_change_password", False) and not user.is_staff:
            allowed_paths = {
                reverse("password_change"),
                reverse("logout"),
            }
            if request.path not in allowed_paths and not request.path.startswith("/admin/"):
                return redirect("password_change")
        return self.get_response(request)
