from django.urls import path
from . import views

urlpatterns = [
    path("get-ticket/<str:slug>", views.buyTickets, name="get_ticket"),
    path("payment/webhook/paystack/", views.paystack_webhook),
    path("payment-success/<str:order_id>/", views.paymentSuccess, name="payment-success"),
]
