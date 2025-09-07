from django.contrib import admin
from.models import Registration, Ticket

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "order_id", "status")

admin.site.register(Ticket)
