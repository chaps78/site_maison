from django.urls import path

from . import views

app_name = "calendrier"

urlpatterns = [
    path("", views.vue_calendrier, name="vue"),
]
