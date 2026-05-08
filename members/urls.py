from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import (
    HomeView,
    MemberProfileView,
    PublicMemberProfileView,
    RequiredPasswordChangeView,
    SignupView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(template_name="members/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password/change/", RequiredPasswordChangeView.as_view(), name="password_change"),
    path("profile/", MemberProfileView.as_view(), name="member_profile"),
    path("members/<str:national_code>/", PublicMemberProfileView.as_view(), name="public_member_profile"),
]
