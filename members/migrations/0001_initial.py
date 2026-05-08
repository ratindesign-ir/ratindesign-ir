import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnnualTariff",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("year", models.PositiveSmallIntegerField(unique=True, verbose_name="سال")),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=0,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                        verbose_name="مبلغ تعرفه",
                    ),
                ),
            ],
            options={
                "verbose_name": "تعرفه سالانه",
                "verbose_name_plural": "تعرفه‌های سالانه",
                "ordering": ["year"],
            },
        ),
        migrations.CreateModel(
            name="Member",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("username", models.CharField(error_messages={"unique": "A user with that username already exists."}, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.", max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name="username")),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.", verbose_name="active")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("national_code", models.CharField(max_length=10, unique=True, verbose_name="کد ملی")),
                ("birth_certificate_number", models.CharField(max_length=32, verbose_name="شماره شناسنامه")),
                ("must_change_password", models.BooleanField(default=True, verbose_name="الزام تغییر رمز در ورود اول")),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={
                "verbose_name": "عضو",
                "verbose_name_plural": "اعضا",
            },
        ),
        migrations.CreateModel(
            name="MemberDebt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=0, default=0, editable=False, max_digits=12, verbose_name="مبلغ محاسبه‌شده")),
                ("description", models.CharField(blank=True, max_length=255, verbose_name="توضیحات")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="debt_records", to="members.member", verbose_name="عضو")),
                ("years", models.ManyToManyField(related_name="member_debts", to="members.annualtariff", verbose_name="سال‌های بدهی")),
            ],
            options={
                "verbose_name": "بدهی عضو",
                "verbose_name_plural": "بدهی‌های اعضا",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=0, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("1"))], verbose_name="مبلغ پرداختی")),
                ("paid_at", models.DateField(verbose_name="تاریخ پرداخت")),
                ("tracking_code", models.CharField(blank=True, max_length=64, verbose_name="کد رهگیری")),
                ("description", models.CharField(blank=True, max_length=255, verbose_name="توضیحات")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="members.member", verbose_name="عضو")),
            ],
            options={
                "verbose_name": "پرداخت",
                "verbose_name_plural": "پرداخت‌ها",
                "ordering": ["-paid_at", "-created_at"],
            },
        ),
    ]
