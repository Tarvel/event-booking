from django import forms
from .models import Events

class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = [
            "title",
            "description",
            "category",
            # "image",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "venue",
            "latitude",
            "longitude",
            "ticket_price",
            "max_capacity",
        ]
