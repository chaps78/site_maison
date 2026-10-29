from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TypeIngredientForm
from .models import TypeIngredient


def liste_recettes(request):
    """Liste des recettes (à construire)."""
    return render(request, "recettes/liste_recettes.html")


@login_required
def types_ingredients_liste(request):
    """Catalogue des ingrédients : pas encore relié aux recettes (voir TypeIngredient)."""
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
    if request.method == "POST":
        type_ingredient.delete()
        return redirect("recettes:types_ingredients_liste")
    return render(
        request, "recettes/type_ingredient_supprimer.html", {"type_ingredient": type_ingredient}
    )
