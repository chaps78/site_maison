from django.urls import path

from . import views

app_name = "recettes"

urlpatterns = [
    path("", views.liste_recettes, name="liste"),
]
