from django import forms
from django.contrib.auth.forms import UserChangeForm

from .models import Member


class MemberCreationForm(forms.ModelForm):
    """Admin form: initial password is set from birth certificate number."""

    class Meta:
        model = Member
        fields = (
            "national_code",
            "birth_certificate_number",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            "is_active",
        )

    def save(self, commit=True):
        member = super().save(commit=False)
        member.username = member.national_code
        member.must_change_password = True
        member.set_password(member.birth_certificate_number)
        if commit:
            member.save()
            self.save_m2m()
        return member


class MemberChangeForm(UserChangeForm):
    class Meta:
        model = Member
        fields = "__all__"


class PublicSignupForm(forms.ModelForm):
    """Register a member with default password equal to birth certificate number."""

    class Meta:
        model = Member
        fields = (
            "national_code",
            "birth_certificate_number",
            "first_name",
            "last_name",
            "email",
        )

    def save(self, commit=True):
        member = super().save(commit=False)
        member.username = member.national_code
        member.must_change_password = True
        member.set_password(member.birth_certificate_number)
        if commit:
            member.save()
        return member
