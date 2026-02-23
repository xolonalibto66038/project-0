# billing/models.py

from django.contrib.auth.models import User
from django.db import models


class StripeCustomer(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="stripe_customer"
    )

    stripe_customer_id = models.CharField(max_length=255, unique=True)

    stripe_subscription_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    subscription_status = models.CharField(
        max_length=50,
        default="inactive"
    )

    current_period_end = models.DateTimeField(
        null=True,
        blank=True
    )

    def is_active(self):
        return self.subscription_status in ("active", "trialing")

    def __str__(self):
        return f"{self.user.username} ({self.subscription_status})"