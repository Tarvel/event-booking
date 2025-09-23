from django.urls import path
from . import views

urlpatterns = [
    path("create-event/", views.create_event, name="create_event"),
    path("edit-event/<str:slug>", views.edit_event, name="edit_event"),
    path("publish/<str:slug>", views.publish_event, name="publish_event"),
    path("my-events/", views.my_events, name="my_events"),
    
    path("", views.home, name="home"),
    path("event/<str:slug>", views.event_detail, name="event_detail"),
    path("download/<str:slug>/", views.download_ticket, name="download_ticket"),
    path("validate-ticket/<str:slug>/", views.validateTicket, name="validate_ticket"),
    
    path("validate-ticket/success/<str:slug>", views.validTik, name="valid_ticket"),
    path("validate-ticket/failure/", views.invalidTik, name="invalid_ticket"),
    path("validate-ticket/used/<str:slug>/", views.usedTik, name="used_ticket"),
    path("check-in/", views.checkPage, name="check_in"),
    
    path("autocomplete/", views.place_autocomplete, name="place_autocomplete"),
]
