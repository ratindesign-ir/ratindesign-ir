from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import MemberChangeForm, MemberCreationForm
from .models import AnnualTariff, Member, MemberDebt, Payment


@admin.register(Member)
class MemberAdmin(UserAdmin):
    form = MemberChangeForm
    add_form = MemberCreationForm
    list_display = (
        "national_code",
        "first_name",
        "last_name",
        "remaining_debt_amount",
        "paid_amount",
        "must_change_password",
        "is_staff",
    )
    search_fields = ("national_code", "first_name", "last_name", "email")
    ordering = ("national_code",)
    readonly_fields = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        (_("اطلاعات عضویت"), {"fields": ("national_code", "birth_certificate_number", "must_change_password")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "national_code",
                    "birth_certificate_number",
                    "first_name",
                    "last_name",
                    "email",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )

    @admin.display(description=_("بدهی باقیمانده"))
    def remaining_debt_amount(self, obj):
        return obj.remaining_debt_amount

    @admin.display(description=_("مبلغ پرداختی"))
    def paid_amount(self, obj):
        return obj.paid_amount


@admin.register(AnnualTariff)
class AnnualTariffAdmin(admin.ModelAdmin):
    list_display = ("year", "amount")
    search_fields = ("year",)
    ordering = ("year",)


@admin.register(MemberDebt)
class MemberDebtAdmin(admin.ModelAdmin):
    list_display = ("member", "selected_years", "amount", "created_at")
    list_filter = ("years", "created_at")
    search_fields = ("member__national_code", "member__first_name", "member__last_name")
    filter_horizontal = ("years",)
    readonly_fields = ("amount", "created_at", "updated_at")
    autocomplete_fields = ("member",)

    @admin.display(description=_("سال‌های انتخابی"))
    def selected_years(self, obj):
        return "، ".join(str(tariff.year) for tariff in obj.years.all())

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.recalculate_amount()


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("member", "amount", "paid_at", "tracking_code")
    list_filter = ("paid_at",)
    search_fields = ("member__national_code", "member__first_name", "member__last_name", "tracking_code")
    autocomplete_fields = ("member",)
