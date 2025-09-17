from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model

User = get_user_model()


class Events(models.Model):
    STATUS_CHOICES = [
        ("other", "Other"),
        ("music", "Music"),
        ("technology", "Technology"),
        ("arts", "Arts & Culture"),
        ("food", "Food & Drink"),
        ("sports", "Sports & Fitness"),
    ]

    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    image = CloudinaryField("image", blank=True, null=True)

    title = models.CharField()
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(choices=STATUS_CHOICES, default="other")

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)

    venue = models.CharField()
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)

    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_ticket = models.IntegerField(null=True, blank=True)
    max_capacity = models.IntegerField(default=0)

    is_published = models.BooleanField(default=False)
    published_at = models.DateField(blank=True, null=True)

    created_at = models.DateField(auto_now_add=True)

    @property
    def ticket_bought(self):
        if self.max_capacity is None or self.available_ticket is None:
            return 0
        return int(self.max_capacity) - int(self.available_ticket)

    @property
    def revenue(self):
        return Decimal(self.ticket_price) * Decimal(self.ticket_bought)

    def save(self, *args, **kwargs):

        if not self.available_ticket:
            self.available_ticket = self.max_capacity

        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1

        while Events.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
