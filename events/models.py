from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Events(models.Model):
    STATUS_CHOICES = [
        ("other", "Other"),
        ("music", "Music"),
        ("technology", "Technology"),
        ("arts", "Arts & Culture"),
        ("food", "Food & Drink"),
    ]

    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField()
    description = models.TextField(null=True, blank=True)
    category = models.CharField(choices=STATUS_CHOICES, default="other")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    venue = models.CharField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_capacity = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
