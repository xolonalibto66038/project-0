import stripe

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse
from django.conf import settings

from .models import StripeCustomer
from .decorators import premium_required
from .services import create_checkout_session
from .webhooks import handle_checkout_session_completed, handle_subscription_created

@login_required
def home(request):

    stripe_customer = getattr(
        request.user,
        "stripe_customer",
        None
    )

    context = {

        "subscription": stripe_customer

    }

    return render(request, "home.html", context)

@premium_required
def premium_dashboard(request):

    return render(request, "dashboard.html")

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@login_required
def create_checkout_session_view(request):

    domain = request.build_absolute_uri("/")[:-1]

    session = create_checkout_session(
        request.user,
        domain
    )

    return JsonResponse({
        "sessionId": session.id
    })


@login_required
def success(request):
    return render(request, 'success.html')


@login_required
def cancel(request):
    return render(request, 'cancel.html')


@csrf_exempt
def stripe_webhook(request):

    payload = request.body

    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_ENDPOINT_SECRET
        )

    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        handle_checkout_session_completed(
            event["data"]["object"]
        )

    elif event["type"] == "customer.subscription.created":
        handle_subscription_created(
            event["data"]["object"]
        )

    elif event["type"] == "customer.subscription.deleted":
        handle_subscription_deleted(event["data"]["object"])

    return HttpResponse(status=200)