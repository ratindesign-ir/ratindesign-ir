from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Member(AbstractUser):
    """Association member who logs in with national code as username."""

    national_code = models.CharField(_("کد ملی"), max_length=10, unique=True)
    birth_certificate_number = models.CharField(_("شماره شناسنامه"), max_length=32)
    must_change_password = models.BooleanField(_("الزام تغییر رمز در ورود اول"), default=True)

    REQUIRED_FIELDS = ["national_code", "birth_certificate_number"]

    class Meta:
        verbose_name = _("عضو")
        verbose_name_plural = _("اعضا")

    def save(self, *args, **kwargs):
        if self.national_code:
            self.username = self.national_code
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("public_member_profile", kwargs={"national_code": self.national_code})

    @property
    def assigned_debt_amount(self):
        return self.debt_records.aggregate(total=Sum("amount"))["total"] or Decimal("0")

    @property
    def paid_amount(self):
        return self.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0")

    @property
    def remaining_debt_amount(self):
        return max(self.assigned_debt_amount - self.paid_amount, Decimal("0"))

    def __str__(self):
        full_name = self.get_full_name()
        return f"{full_name} ({self.national_code})" if full_name else self.national_code


class AnnualTariff(models.Model):
    """Yearly fixed tariff shared by all members."""

    year = models.PositiveSmallIntegerField(_("سال"), unique=True)
    amount = models.DecimalField(
        _("مبلغ تعرفه"),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        ordering = ["year"]
        verbose_name = _("تعرفه سالانه")
        verbose_name_plural = _("تعرفه‌های سالانه")

    def __str__(self):
        return f"{self.year} - {self.amount:,.0f} ریال"


class MemberDebt(models.Model):
    """Debt assigned to one member for one or more selected years."""

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="debt_records",
        verbose_name=_("عضو"),
    )
    years = models.ManyToManyField(
        AnnualTariff,
        related_name="member_debts",
        verbose_name=_("سال‌های بدهی"),
    )
    amount = models.DecimalField(
        _("مبلغ محاسبه‌شده"),
        max_digits=12,
        decimal_places=0,
        default=0,
        editable=False,
    )
    description = models.CharField(_("توضیحات"), max_length=255, blank=True)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("آخرین بروزرسانی"), auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("بدهی عضو")
        verbose_name_plural = _("بدهی‌های اعضا")

    def recalculate_amount(self, save=True):
        self.amount = self.years.aggregate(total=Sum("amount"))["total"] or Decimal("0")
        if save and self.pk:
            self.save(update_fields=["amount", "updated_at"])
        return self.amount

    def __str__(self):
        return f"{self.member} - {self.amount:,.0f} ریال"


class Payment(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("عضو"),
    )
    amount = models.DecimalField(
        _("مبلغ پرداختی"),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("1"))],
    )
    paid_at = models.DateField(_("تاریخ پرداخت"))
    tracking_code = models.CharField(_("کد رهگیری"), max_length=64, blank=True)
    description = models.CharField(_("توضیحات"), max_length=255, blank=True)
    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)

    class Meta:
        ordering = ["-paid_at", "-created_at"]
        verbose_name = _("پرداخت")
        verbose_name_plural = _("پرداخت‌ها")

    def __str__(self):
        return f"{self.member} - {self.amount:,.0f} ریال"
