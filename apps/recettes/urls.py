from django.urls import path

from . import views

app_name = "recettes"

urlpatterns = [
    path("", views.liste_recettes, name="liste"),
    path("ajouter/", views.recette_creer, name="recette_creer"),
    path("ingredients/", views.types_ingredients_liste, name="types_ingredients_liste"),
    path("ingredients/ajouter/", views.type_ingredient_creer, name="type_ingredient_creer"),
    path(
        "ingredients/<int:pk>/modifier/",
        views.type_ingredient_modifier,
        name="type_ingredient_modifier",
    ),
    path(
        "ingredients/<int:pk>/supprimer/",
        views.type_ingredient_supprimer,
        name="type_ingredient_supprimer",
    ),
    path("<int:pk>/", views.recette_detail, name="recette_detail"),
    path("<int:pk>/modifier/", views.recette_modifier, name="recette_modifier"),
]
