# billing/webhooks.py

import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from .models import StripeCustomer
from .services import retrieve_subscription

stripe.api_key = settings.STRIPE_SECRET_KEY


def handle_checkout_session_completed(session):

    user_id = session.get("client_reference_id")

    stripe_customer_id = session.get("customer")

    stripe_subscription_id = session.get("subscription")

    if not stripe_subscription_id:
        raise ValueError("No subscription ID found in session")

    user = User.objects.get(id=user_id)

    subscription = retrieve_subscription(stripe_subscription_id)

    # Safely access period end
    current_period_end = None

    if getattr(subscription, "current_period_end", None) and subscription.current_period_end:

        current_period_end = timezone.datetime.fromtimestamp(
            subscription.current_period_end,
            tz=timezone.utc
        )

    StripeCustomer.objects.update_or_create(

        user=user,

        defaults={

            "stripe_customer_id": stripe_customer_id,

            "stripe_subscription_id": stripe_subscription_id,

            "subscription_status": subscription.status,

            "current_period_end": current_period_end
        },
    )


def handle_subscription_created(subscription_event):

    subscription_id = subscription_event.get("id")

    stripe_customer_id = subscription_event.get("customer")

    # Always retrieve full subscription from Stripe
    subscription = retrieve_subscription(subscription_id)

    # Convert timestamp safely
    current_period_end = None

    timestamp = subscription.get("current_period_end")

    if timestamp:
        current_period_end = timezone.datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc
        )

    # Try to find existing StripeCustomer
    stripe_customer = StripeCustomer.objects.filter(
        stripe_customer_id=stripe_customer_id
    ).first()

    if stripe_customer:

        # Update existing
        stripe_customer.stripe_subscription_id = subscription_id
        stripe_customer.subscription_status = subscription.status
        stripe_customer.current_period_end = current_period_end
        stripe_customer.save()

    else:

        # Create new (webhook order not guaranteed)

        # Retrieve customer from Stripe to find user
        stripe_customer_obj = stripe.Customer.retrieve(stripe_customer_id)

        user_id = stripe_customer_obj.get("metadata", {}).get("user_id")

        if not user_id:
            return

        user = User.objects.get(id=user_id)

        StripeCustomer.objects.create(

            user=user,

            stripe_customer_id=stripe_customer_id,

            stripe_subscription_id=subscription_id,

            subscription_status=subscription.status,

            current_period_end=current_period_end,
        )


def handle_subscription_deleted(subscription_event):
    """
    Handles Stripe customer.subscription.deleted webhook.
    Marks subscription as inactive in our database.
    """

    subscription_id = subscription_event.get("id")
    stripe_customer_id = subscription_event.get("customer")

    if not subscription_id or not stripe_customer_id:
        return

    try:
        stripe_customer = StripeCustomer.objects.get(
            stripe_customer_id=stripe_customer_id
        )
    except StripeCustomer.DoesNotExist:
        return  # silently ignore (safe for portfolio project)

    # Optional but recommended: retrieve full subscription for safety
    try:
        subscription = retrieve_subscription(subscription_id)
        status = subscription.status
    except Exception:
        # If Stripe retrieval fails, assume canceled
        status = "canceled"

    stripe_customer.subscription_status = status
    timestamp = subscription_event.get("canceled_at")

    if timestamp:
        stripe_customer.current_period_end = timezone.datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc
        )
    stripe_customer.save()