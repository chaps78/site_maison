from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("connexion/", views.connexion, name="connexion"),
    path("connexion/<str:username>/", views.connexion_code, name="connexion_code"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
    path("profils/", views.profils_liste, name="profils_liste"),
    path("profils/ajouter/", views.profil_creer, name="profil_creer"),
    path("profils/<int:pk>/modifier/", views.profil_modifier, name="profil_modifier"),
    path("profils/<int:pk>/supprimer/", views.profil_supprimer, name="profil_supprimer"),
]
