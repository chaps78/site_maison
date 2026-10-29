from django.urls import path

from . import views

app_name = "taches"

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("historique/", views.historique, name="historique"),
    path("catalogue/", views.catalogue, name="catalogue"),
    path("catalogue/ajouter/", views.catalogue_ajouter, name="catalogue_ajouter"),
    path("catalogue/<int:pk>/modifier/", views.catalogue_modifier, name="catalogue_modifier"),
    path("catalogue/<int:pk>/basculer/", views.catalogue_basculer, name="catalogue_basculer"),
    path("<int:pk>/supprimer/", views.effectuee_supprimer, name="effectuee_supprimer"),
]
