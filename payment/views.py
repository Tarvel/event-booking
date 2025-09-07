import json
import uuid
from django.conf import settings
from payment.paystack import checkout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from notifications.models import Notification
from booking.models import Registration, Ticket
from events.models import Events
from .models import Payment
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import hmac
import hashlib
from django.db.models import F


User = get_user_model()


def paymentSuccess(request, order_id):
    try:
        registration = Registration.objects.get(order_id=order_id)
    except Registration.DoesNotExist:
        messages.error(request, "Payment failed")
        return redirect("home")

    return render(
        request, "payment/payment_success.html", {"registration": registration}
    )


@login_required
def buyTickets(request, slug):
    if request.user.is_authenticated:
        user = request.user
    else:
        return redirect("login")

    event = Events.objects.get(slug=slug)
    # generate unique ids for order and payment reference
    unique_order_id = f"ORD-{str(uuid.uuid4())[0:9]}"
    unique_reference_id = f"ref-{str(uuid.uuid4())[0:8]}"
    unique_code = f"TIK-{str(uuid.uuid4())[0:8]}"

    # Createing registration
    registration = Registration.objects.create(
        user=user,
        event=event,
        order_id=unique_order_id,
        reference=unique_reference_id,
        status="pending",
    )

    print(registration.user.first_name, registration.reference)

    print("Registratin created")

    # create the ticket instance(?)
    # ticket = Ticket.objects.create(registration=registration, unique_code=unique_code)
    #

    # Build callback URL
    payment_success_url = reverse(
        "payment-success", kwargs={"order_id": registration.order_id}
    )
    callback_url = f"{request.scheme}://{request.get_host()}{payment_success_url}"

    checkout_data = {
        "email": user.email or user.username,
        "amount": int(registration.event.ticket_price * 100),  # convert to kobo
        "currency": "NGN",
        "channels": ["card", "bank_transfer", "bank", "ussd", "qr", "mobile_money"],
        "reference": str(registration.reference),
        "callback_url": callback_url,
        "metadata": {
            "order_id": str(registration.order_id),
            "user_id": user.id,
            "payment_reference": registration.reference,
        },
        "label": f"Checkout For order: {registration.event.title}-{registration.order_id}",
    }

    # Call checkout logic
    status, checkout_url, payment_reference = checkout(checkout_data)

    print(payment_reference)

    if status:
        # if the connection to paystack is sucessful, update the registration status to pending (default), cos, technically, the payment is in a pending state unless payment is scuessful
        # we will get this success status from our webhook

        return redirect(checkout_url)

    else:
        # if theres an error, first update the order status and time the error in payment occured, then make a failed payment instance sha

        registration.status = "failed"
        registration.updated_at = timezone.now()

        payment = Payment.objects.create(
            registration=registration,
            user=user,
            payment_reference=registration.reference,
            amount=registration.event.ticket_price,
            status="failed",
            paid_at=timezone.now(),
        )

        messages.error(request, checkout_url)  # Shows error message
        return redirect("payment-fail", registration.order_id)


@csrf_exempt
def paystack_webhook(request):
    print("testing webok")
    secret = settings.PAYSTACK_SECRET_KEY
    request_body = request.body

    hash = hmac.new(secret.encode("utf-8"), request_body, hashlib.sha512).hexdigest()

    if hash == request.META.get("HTTP_X_PAYSTACK_SIGNATURE"):
        webhook_post_data = json.loads(request_body)
        print(f"This is data: {webhook_post_data}")

        if webhook_post_data["event"] == "charge.success":
            metadata = webhook_post_data["data"]["metadata"]

            # get oder_id and user_id to retrive their respective instances, then get payment_reference to populate the newly created Payment instance
            order_id = metadata["order_id"]
            user_id = metadata["user_id"]
            payment_reference = metadata["payment_reference"]

            # retrive registration and user instances then add them to the newly created Payment instance
            registration = Registration.objects.get(order_id=order_id)
            event = Events.objects.filter(slug=registration.event.slug).first()
            user = User.objects.get(id=user_id)

            registration.updated_at = timezone.now()
            registration.status = "approved"
            registration.save(update_fields=["updated_at", "status"])
            registration.refresh_from_db()

            event.available_ticket = F("available_ticket") - 1
            event.save(update_fields=["available_ticket"])
            event.refresh_from_db()

            unique_code = f"TIK-{str(uuid.uuid4())[0:8]}"
            ticket = Ticket.objects.create(
                registration=registration, unique_code=unique_code
            )

            notification = Notification.objects.create(
                user=user,
                notification_type="ticket_ready",
                registration=registration,
            )

            payment = Payment.objects.create(
                registration=registration,
                user=user,
                payment_reference=payment_reference,
                amount=registration.event.ticket_price,
                status="success",
                paid_at=timezone.now(),
            )

    return HttpResponse(status=200)
