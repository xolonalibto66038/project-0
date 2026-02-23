# billing/services.py

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(user, domain):

    return stripe.checkout.Session.create(

        client_reference_id=user.id,

        metadata={
            "user_id": user.id
        },

        success_url=f"{domain}/success?session_id={{CHECKOUT_SESSION_ID}}",

        cancel_url=f"{domain}/cancel/",

        payment_method_types=["card"],

        mode="subscription",

        line_items=[
            {
                "price": settings.STRIPE_PRICE_ID,
                "quantity": 1,
            }
        ],
    )


def retrieve_subscription(subscription_id):

    return stripe.Subscription.retrieve(subscription_id)