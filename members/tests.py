from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AnnualTariff, MemberDebt, Payment


class DebtCalculationTests(TestCase):
    def setUp(self):
        self.member = get_user_model().objects.create_user(
            username="0012345678",
            national_code="0012345678",
            birth_certificate_number="1234",
            password="1234",
        )
        self.tariff_1402 = AnnualTariff.objects.create(year=1402, amount=Decimal("1000000"))
        self.tariff_1403 = AnnualTariff.objects.create(year=1403, amount=Decimal("1500000"))

    def test_member_debt_amount_is_sum_of_selected_years(self):
        debt = MemberDebt.objects.create(member=self.member)
        debt.years.set([self.tariff_1402, self.tariff_1403])
        debt.refresh_from_db()

        self.assertEqual(debt.amount, Decimal("2500000"))
        self.assertEqual(self.member.assigned_debt_amount, Decimal("2500000"))

    def test_remaining_debt_subtracts_payments(self):
        debt = MemberDebt.objects.create(member=self.member)
        debt.years.set([self.tariff_1402, self.tariff_1403])
        Payment.objects.create(member=self.member, amount=Decimal("700000"), paid_at=date(2026, 5, 8))

        self.assertEqual(self.member.remaining_debt_amount, Decimal("1800000"))


class AuthenticationFlowTests(TestCase):
    def test_signup_uses_national_code_and_birth_certificate_as_initial_credentials(self):
        response = self.client.post(
            reverse("signup"),
            {
                "national_code": "0098765432",
                "birth_certificate_number": "5678",
                "first_name": "علی",
                "last_name": "رضایی",
                "email": "ali@example.com",
            },
        )

        self.assertRedirects(response, reverse("login"))
        member = get_user_model().objects.get(national_code="0098765432")
        self.assertEqual(member.username, "0098765432")
        self.assertTrue(member.check_password("5678"))
        self.assertTrue(member.must_change_password)

    def test_first_login_is_redirected_to_password_change_until_updated(self):
        member = get_user_model().objects.create_user(
            username="0011111111",
            national_code="0011111111",
            birth_certificate_number="2222",
            password="2222",
            must_change_password=True,
        )

        self.client.force_login(member)
        response = self.client.get(reverse("member_profile"))
        self.assertRedirects(response, reverse("password_change"))

        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": "2222",
                "new_password1": "StrongPass123!",
                "new_password2": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("member_profile"))
        member.refresh_from_db()
        self.assertFalse(member.must_change_password)
        self.assertTrue(member.check_password("StrongPass123!"))
