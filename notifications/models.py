from django.db import models
from booking.models import Registration
from django.utils import timezone
from django.contrib.auth import get_user_model


AuthUser = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("event_reminder", "Event Reminder"),
        ("ticket_ready", "Ticket Ready"),
        ("new_event", "New Event"),
    ]

    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField(default="notif") 
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.notification_type}"
