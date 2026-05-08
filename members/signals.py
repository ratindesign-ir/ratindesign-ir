from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import MemberDebt


@receiver(m2m_changed, sender=MemberDebt.years.through)
def update_member_debt_amount(sender, instance, action, **kwargs):
    if action in {"post_add", "post_remove", "post_clear"}:
        instance.recalculate_amount()
