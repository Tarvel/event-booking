from django.db import models
from django.utils import timezone
from django.utils.text import slugify
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
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(choices=STATUS_CHOICES, default="other")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    venue = models.CharField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_ticket = models.IntegerField(null=True, blank=True)
    max_capacity = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Events.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
