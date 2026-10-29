import calendar
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.core.models import User

from .forms import TacheRapideForm, TypeTacheForm
from .models import TacheEffectuee, TypeTache


@login_required
def accueil(request):
    """Ajout rapide d'une tâche faite aujourd'hui (parents) + liste du jour (tout le monde)."""
    form = None
    if request.user.est_parent:
        form = TacheRapideForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            TacheEffectuee.objects.create(
                enfant=form.cleaned_data["enfant"],
                type_tache=form.cleaned_data["type_tache"],
                # Jour local (Buenos Aires) : jamais date.today(), voir le fuseau du projet.
                date=timezone.localdate(),
                created_by=request.user,
            )
            return redirect("taches:accueil")
    elif request.method == "POST":
        raise PermissionDenied("Seul un parent peut enregistrer une tâche.")

    aujourdhui = timezone.localdate()
    taches_du_jour = (
        TacheEffectuee.objects.filter(date=aujourdhui)
        .select_related("enfant", "type_tache")
        .order_by("enfant__ordre", "-created_at")
    )
    return render(
        request,
        "taches/accueil.html",
        {"form": form, "taches_du_jour": taches_du_jour, "aujourdhui": aujourdhui},
    )


@login_required
def historique(request):
    """Vue mensuelle : total de points par enfant + détail jour par jour, mois navigable."""
    aujourdhui = timezone.localdate()
    annee = int(request.GET.get("annee", aujourdhui.year))
    mois = int(request.GET.get("mois", aujourdhui.month))
    premier_jour_du_mois = date(annee, mois, 1)
    dernier_jour_du_mois = date(annee, mois, calendar.monthrange(annee, mois)[1])

    taches_du_mois = (
        TacheEffectuee.objects.filter(date__year=annee, date__month=mois)
        .select_related("enfant", "type_tache")
        .order_by("-date", "enfant__ordre")
    )

    # Un enfant qui n'a rien fait ce mois-ci doit tout de même apparaître, avec 0 point.
    enfants_totaux = (
        User.objects.filter(is_staff=False, est_parent=False)
        .order_by("ordre", "first_name")
        .annotate(
            total=Coalesce(
                Sum(
                    "taches_effectuees__type_tache__points",
                    filter=Q(
                        taches_effectuees__date__year=annee, taches_effectuees__date__month=mois
                    ),
                ),
                0,
            )
        )
    )

    mois_precedent = premier_jour_du_mois - timedelta(days=1)
    mois_suivant = dernier_jour_du_mois + timedelta(days=1)
    return render(
        request,
        "taches/historique.html",
        {
            "taches_du_mois": taches_du_mois,
            "enfants_totaux": enfants_totaux,
            "premier_jour_du_mois": premier_jour_du_mois,
            "mois_precedent": mois_precedent,
            "mois_suivant": mois_suivant,
        },
    )


@login_required
def catalogue(request):
    """Liste du catalogue de tâches, visible par tous ; seuls les parents le modifient."""
    types = TypeTache.objects.all().order_by("nom")
    return render(request, "taches/catalogue.html", {"types": types})


@login_required
def catalogue_ajouter(request):
    if not request.user.est_parent:
        raise PermissionDenied("Seul un parent peut gérer le catalogue.")
    form = TypeTacheForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("taches:catalogue")
    return render(
        request, "taches/type_tache_form.html", {"form": form, "titre": "Ajouter une tâche"}
    )


@login_required
def catalogue_modifier(request, pk):
    if not request.user.est_parent:
        raise PermissionDenied("Seul un parent peut gérer le catalogue.")
    type_tache = get_object_or_404(TypeTache, pk=pk)
    form = TypeTacheForm(request.POST or None, instance=type_tache)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("taches:catalogue")
    return render(
        request,
        "taches/type_tache_form.html",
        {"form": form, "titre": f"Modifier « {type_tache.nom} »"},
    )


@login_required
def catalogue_basculer(request, pk):
    """Active/désactive une tâche du catalogue (jamais de suppression : voir TacheEffectuee)."""
    if not request.user.est_parent:
        raise PermissionDenied("Seul un parent peut gérer le catalogue.")
    type_tache = get_object_or_404(TypeTache, pk=pk)
    if request.method == "POST":
        type_tache.actif = not type_tache.actif
        type_tache.save()
    return redirect("taches:catalogue")


@login_required
def effectuee_supprimer(request, pk):
    """Retire une tâche enregistrée par erreur (réservé aux parents)."""
    if not request.user.est_parent:
        raise PermissionDenied("Seul un parent peut supprimer une tâche enregistrée.")
    tache = get_object_or_404(TacheEffectuee, pk=pk)
    if request.method == "POST":
        tache.delete()
        return redirect("taches:accueil")
    return render(request, "taches/effectuee_supprimer.html", {"tache": tache})
