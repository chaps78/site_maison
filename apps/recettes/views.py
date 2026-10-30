from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    IngredientFormSetCreation,
    IngredientFormSetModification,
    RecetteForm,
    TypeIngredientForm,
)
from .models import Recette, TypeIngredient


def liste_recettes(request):
    """Liste des recettes : juste les titres pour l'instant."""
    recettes = Recette.objects.all()
    return render(request, "recettes/liste_recettes.html", {"recettes": recettes})


@login_required
def recette_detail(request, pk):
    """Titre, ingrédients et commentaire d'une recette, avec un bouton Modifier."""
    recette = get_object_or_404(Recette, pk=pk)
    return render(request, "recettes/recette_detail.html", {"recette": recette})


@login_required
def recette_creer(request):
    """Création d'une recette : titre, commentaires, et jusqu'à 10 lignes d'ingrédients."""
    recette_form = RecetteForm(request.POST or None)
    formset = IngredientFormSetCreation(request.POST or None, instance=Recette())
    if request.method == "POST" and recette_form.is_valid() and formset.is_valid():
        recette = recette_form.save(commit=False)
        recette.created_by = request.user
        recette.save()
        formset.instance = recette
        formset.save()
        return redirect("recettes:recette_detail", pk=recette.pk)
    return render(
        request,
        "recettes/recette_form.html",
        {"recette_form": recette_form, "formset": formset, "titre": "Créer une recette"},
    )


@login_required
def recette_modifier(request, pk):
    """Modification d'une recette existante : mêmes champs que la création."""
    recette = get_object_or_404(Recette, pk=pk)
    recette_form = RecetteForm(request.POST or None, instance=recette)
    formset = IngredientFormSetModification(request.POST or None, instance=recette)
    if request.method == "POST" and recette_form.is_valid() and formset.is_valid():
        recette_form.save()
        formset.save()
        return redirect("recettes:recette_detail", pk=recette.pk)
    return render(
        request,
        "recettes/recette_form.html",
        {
            "recette_form": recette_form,
            "formset": formset,
            "titre": f"Modifier « {recette.titre} »",
        },
    )


@login_required
def recette_supprimer(request, pk):
    recette = get_object_or_404(Recette, pk=pk)
    if request.method == "POST":
        recette.delete()
        return redirect("recettes:liste")
    return render(request, "recettes/recette_supprimer.html", {"recette": recette})


@login_required
def types_ingredients_liste(request):
    """Catalogue des ingrédients, utilisé pour composer les recettes (voir Ingredient)."""
    types = TypeIngredient.objects.all()
    return render(request, "recettes/types_ingredients_liste.html", {"types": types})


@login_required
def type_ingredient_creer(request):
    form = TypeIngredientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("recettes:types_ingredients_liste")
    return render(
        request,
        "recettes/type_ingredient_form.html",
        {"form": form, "titre": "Ajouter un type d'ingrédient"},
    )


@login_required
def type_ingredient_modifier(request, pk):
    type_ingredient = get_object_or_404(TypeIngredient, pk=pk)
    form = TypeIngredientForm(request.POST or None, instance=type_ingredient)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("recettes:types_ingredients_liste")
    return render(
        request,
        "recettes/type_ingredient_form.html",
        {"form": form, "titre": f"Modifier « {type_ingredient.nom} »"},
    )


@login_required
def type_ingredient_supprimer(request, pk):
    type_ingredient = get_object_or_404(TypeIngredient, pk=pk)
    erreur = None
    if request.method == "POST":
        try:
            type_ingredient.delete()
            return redirect("recettes:types_ingredients_liste")
        except ProtectedError:
            # Utilisé dans au moins une recette (PROTECT) : on affiche un message propre
            # plutôt que de laisser remonter une erreur 500.
            erreur = "Cet ingrédient est utilisé dans une recette : impossible de le supprimer."
    return render(
        request,
        "recettes/type_ingredient_supprimer.html",
        {"type_ingredient": type_ingredient, "erreur": erreur},
    )
