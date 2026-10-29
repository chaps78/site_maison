from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required, login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CodeForm, ConnexionForm, ProfilForm
from .models import User


def accueil(request):
    """Page d'accueil : liens vers les sections du site."""
    return render(request, "core/accueil.html")


@login_not_required
def connexion(request):
    """Écran de connexion : un bouton par profil du foyer (pas de champ identifiant)."""
    if request.user.is_authenticated:
        return redirect("core:accueil")
    profils = User.objects.filter(is_staff=False, is_active=True).order_by("ordre", "first_name")
    return render(request, "core/connexion.html", {"profils": profils})


@login_not_required
def connexion_code(request, username):
    """Saisie du code à 4 chiffres pour le profil choisi à l'étape précédente."""
    if request.user.is_authenticated:
        return redirect("core:accueil")
    profil = get_object_or_404(User, username=username, is_staff=False, is_active=True)
    erreur = False
    form = ConnexionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        utilisateur = authenticate(request, username=username, password=form.cleaned_data["code"])
        if utilisateur is not None:
            login(request, utilisateur)
            return redirect("core:accueil")
        erreur = True
    return render(
        request,
        "core/connexion_code.html",
        {"profil": profil, "form": form, "erreur": erreur},
    )


@require_POST
def deconnexion(request):
    """Déconnexion : toujours par bouton (POST), jamais par simple lien GET."""
    logout(request)
    return redirect("core:connexion")


@login_required
def profils_liste(request):
    """CRUD des profils du foyer : volontairement séparé de /admin/ (voir ProfilForm).

    Visible par tout le monde (foyer partagé), mais seul un administrateur (est_admin) voit
    les actions d'ajout/suppression et peut modifier le profil de quelqu'un d'autre.
    """
    profils = User.objects.filter(is_staff=False).order_by("ordre", "first_name")
    return render(request, "core/profils_liste.html", {"profils": profils})


@login_required
def profil_creer(request):
    if not request.user.est_admin:
        raise PermissionDenied("Seul un administrateur du foyer peut ajouter un profil.")
    form = ProfilForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("core:profils_liste")
    return render(request, "core/profil_form.html", {"form": form, "titre": "Ajouter un profil"})


@login_required
def profil_modifier(request, pk):
    """Un administrateur modifie n'importe quel profil ; les autres, seulement le leur
    (et seulement leur code, pas leur prénom ni leur statut : voir CodeForm)."""
    profil = get_object_or_404(User, pk=pk, is_staff=False)
    est_admin = request.user.est_admin
    est_soi_meme = profil.pk == request.user.pk
    if not est_admin and not est_soi_meme:
        raise PermissionDenied("Tu ne peux changer que ton propre code.")

    if est_admin:
        form = ProfilForm(request.POST or None, instance=profil)
    else:
        form = CodeForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        if est_admin:
            form.save()
        else:
            profil.set_password(form.cleaned_data["code"])
            profil.save()
        return redirect("core:profils_liste")
    return render(
        request,
        "core/profil_form.html",
        {"form": form, "titre": f"Modifier {profil.first_name}"},
    )


@login_required
def profil_supprimer(request, pk):
    if not request.user.est_admin:
        raise PermissionDenied("Seul un administrateur du foyer peut supprimer un profil.")
    profil = get_object_or_404(User, pk=pk, is_staff=False)
    # On évite qu'une personne se supprime elle-même en cours de session
    # (elle resterait connectée avec un compte qui n'existe plus dans la liste).
    se_supprime_soi_meme = profil == request.user
    if request.method == "POST" and not se_supprime_soi_meme:
        profil.delete()
        return redirect("core:profils_liste")
    return render(
        request,
        "core/profil_supprimer.html",
        {"profil": profil, "se_supprime_soi_meme": se_supprime_soi_meme},
    )
