from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.recettes.models import Ingredient, Recette

from .forms import VoteForm
from .models import EtatCourses, Vote


def _resultats_du_jour(date):
    """Un plat par entrée, avec qui a voté pour lui, à quel rang, et le total de points.
    Triés par total décroissant (le plat en tête est le plus plébiscité)."""
    votes = Vote.objects.filter(date=date).select_related(
        "votant", "premier_choix", "deuxieme_choix", "troisieme_choix"
    )
    resultats = {}
    for vote in votes:
        for rang, recette, points in vote.choix_classes:
            entree = resultats.setdefault(
                recette.id, {"recette": recette, "votants": [], "total": 0}
            )
            entree["votants"].append({"votant": vote.votant, "rang": rang, "points": points})
            entree["total"] += points
    return sorted(resultats.values(), key=lambda e: -e["total"])


@login_required
def accueil(request):
    """Vote du jour (1 à 3 plats classés) + résultats, visibles de tout le foyer."""
    aujourdhui = timezone.localdate()
    mon_vote = Vote.objects.filter(votant=request.user, date=aujourdhui).first()
    form = VoteForm(request.POST or None, instance=mon_vote)

    if request.method == "POST" and form.is_valid():
        vote = form.save(commit=False)
        vote.votant = request.user
        vote.date = aujourdhui
        vote.save()
        return redirect("diner:accueil")

    resultats = _resultats_du_jour(aujourdhui)
    for entree in resultats:
        etat, _ = EtatCourses.objects.get_or_create(recette=entree["recette"], date=aujourdhui)
        entree["etat_courses"] = etat
        entree["ingredients"] = entree["recette"].ingredients.select_related("type_ingredient")

    return render(
        request,
        "diner/accueil.html",
        {"form": form, "resultats": resultats, "aujourdhui": aujourdhui},
    )


@login_required
def courses_basculer(request, recette_pk):
    """Bascule « courses à faire » pour un plat du jour (visible de tout le foyer)."""
    recette = get_object_or_404(Recette, pk=recette_pk)
    aujourdhui = timezone.localdate()
    etat, _ = EtatCourses.objects.get_or_create(recette=recette, date=aujourdhui)
    if request.method == "POST":
        etat.courses_a_faire = not etat.courses_a_faire
        etat.save()
    return redirect("diner:accueil")


@login_required
def ingredients_manquants_modifier(request, recette_pk):
    """Enregistre, pour le plat et le jour en cours, quels ingrédients manquent."""
    recette = get_object_or_404(Recette, pk=recette_pk)
    aujourdhui = timezone.localdate()
    etat, _ = EtatCourses.objects.get_or_create(recette=recette, date=aujourdhui)
    if request.method == "POST":
        ids_coches = request.POST.getlist("manquant")
        etat.ingredients_manquants.set(
            Ingredient.objects.filter(pk__in=ids_coches, recette=recette)
        )
    return redirect("diner:accueil")
