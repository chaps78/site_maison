from django.urls import path

from . import views

app_name = "diner"

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("<int:recette_pk>/courses/basculer/", views.courses_basculer, name="courses_basculer"),
    path(
        "<int:recette_pk>/ingredients-manquants/",
        views.ingredients_manquants_modifier,
        name="ingredients_manquants_modifier",
    ),
]
