import uuid
from django.db import models

from events.models import Events
from django.contrib.auth import get_user_model

User = get_user_model()


class Registration(models.Model):
    unique_id = str(uuid.uuid4())[0:5]
    def_ord = f"ORD-{unique_id}"
    def_ref = f"REF-{unique_id}"
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("denied", "Denied"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    order_id = models.CharField(default=def_ord, unique=True, blank=True)
    reference = models.CharField(default=def_ref, unique=True)
    status = models.CharField(choices=STATUS_CHOICES)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        while Registration.objects.filter(order_id=self.order_id).exclude(pk=self.pk).exists():
            unique_id = str(uuid.uuid4())[0:5]
            order_id = f"ord-{unique_id}"
            self.order_id = order_id

        while Registration.objects.filter(reference=self.reference).exclude(pk=self.pk).exists():
            unique_id = str(uuid.uuid4())[0:5]
            reference = f"ref-{unique_id}"
            self.reference = reference

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} {self.event.title}"


class Ticket(models.Model):
    unique_id = str(uuid.uuid4())[0:5]
    uni_code = f"TIK-{unique_id}"

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    unique_code = models.CharField(unique=True, default=uni_code)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    scanned_date = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        while Ticket.objects.filter(unique_code=self.unique_code).exclude(pk=self.pk).exists():
            unique_id = str(uuid.uuid4())[0:8]
            unique_code = f"TIK-{unique_id}"

            self.unique_code = unique_code

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.registration.event.title}"
