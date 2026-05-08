from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView

from .forms import PublicSignupForm
from .models import Member


class HomeView(TemplateView):
    template_name = "members/home.html"


class SignupView(CreateView):
    model = Member
    form_class = PublicSignupForm
    template_name = "members/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        messages.success(
            self.request,
            "عضویت ثبت شد. اکنون با کد ملی و شماره شناسنامه وارد شوید و رمز را تغییر دهید.",
        )
        return super().form_valid(form)


class MemberProfileView(LoginRequiredMixin, TemplateView):
    template_name = "members/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = self.request.user
        context.update(
            {
                "member": member,
                "debt_records": member.debt_records.prefetch_related("years"),
                "payments": member.payments.all(),
            }
        )
        return context


class PublicMemberProfileView(DetailView):
    model = Member
    template_name = "members/public_profile.html"
    context_object_name = "member"
    slug_field = "national_code"
    slug_url_kwarg = "national_code"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = self.object
        context.update(
            {
                "debt_records": member.debt_records.prefetch_related("years"),
                "payments": member.payments.all(),
            }
        )
        return context


class RequiredPasswordChangeView(PasswordChangeView):
    template_name = "members/password_change.html"
    success_url = reverse_lazy("member_profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.user.must_change_password = False
        self.request.user.save(update_fields=["must_change_password"])
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "رمز عبور با موفقیت تغییر کرد.")
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.must_change_password:
            messages.info(request, "رمز عبور شما قبلاً تغییر کرده است.")
            return redirect("member_profile")
        return super().dispatch(request, *args, **kwargs)
