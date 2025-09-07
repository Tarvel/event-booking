from django.db import models
from booking.models import Registration
from django.contrib.auth import get_user_model

User = get_user_model()


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    registration = models.ForeignKey(
        Registration, on_delete=models.CASCADE, related_name="payments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_reference = models.CharField(max_length=100, unique=False, default="None")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_reference} for Order #{self.registration.order_id}"
