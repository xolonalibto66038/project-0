# billing/decorators.py

from functools import wraps
from django.shortcuts import redirect


def premium_required(view_func):

    @wraps(view_func)

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("account_login")

        stripe_customer = getattr(
            request.user,
            "stripe_customer",
            None
        )

        if stripe_customer and stripe_customer.is_active():
            return view_func(request, *args, **kwargs)

        return redirect("subscriptions-home")

    return wrapper