from django.urls import path

from . import views

app_name = "revisions"

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("multiplications/", views.multiplication_config, name="multiplication_config"),
    path("multiplications/jouer/", views.multiplication_jouer, name="multiplication_jouer"),
    path(
        "multiplications/resultat/",
        views.multiplication_resultat,
        name="multiplication_resultat",
    ),
    path(
        "multiplications/statistiques/",
        views.multiplication_statistiques,
        name="multiplication_statistiques",
    ),
]
