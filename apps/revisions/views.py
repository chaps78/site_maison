import random
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.core.models import User

from .couleurs import couleur_pour_taux
from .forms import ChoixTablesForm
from .models import StatistiqueMultiplication

CLE_SESSION = "quiz_multiplication"
NB_QUESTIONS = 10
# L'autre facteur (pas forcément dans les tables choisies) : convention « tables de 1 à 10 ».
AUTRE_FACTEUR_MIN, AUTRE_FACTEUR_MAX = 1, 10


@login_required
def accueil(request):
    """Liste des exercices de révision disponibles (un seul pour l'instant)."""
    return render(request, "revisions/accueil.html")


@login_required
def multiplication_config(request):
    """Demande les tables à réviser avant de démarrer le quiz."""
    form = ChoixTablesForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        tables = form.cleaned_data["tables"]
        questions = [
            [random.choice(tables), random.randint(AUTRE_FACTEUR_MIN, AUTRE_FACTEUR_MAX)]
            for _ in range(NB_QUESTIONS)
        ]
        request.session[CLE_SESSION] = {
            "questions": questions,
            "index": 0,
            "reussites": 0,
            "temps": [],
            "debut_question": timezone.now().isoformat(),
        }
        return redirect("revisions:multiplication_jouer")
    return render(request, "revisions/multiplication_config.html", {"form": form})


@login_required
def multiplication_jouer(request):
    """Affiche la question en cours (GET) et valide la réponse (POST)."""
    quiz = request.session.get(CLE_SESSION)
    if not quiz or quiz["index"] >= NB_QUESTIONS:
        return redirect("revisions:multiplication_config")

    a, b = quiz["questions"][quiz["index"]]

    if request.method == "POST":
        debut = datetime.fromisoformat(quiz["debut_question"])
        maintenant = timezone.now()
        duree = (maintenant - debut).total_seconds()
        try:
            reponse = int(request.POST.get("reponse", ""))
        except ValueError:
            reponse = None
        reussi = reponse == a * b

        StatistiqueMultiplication.enregistrer_resultat(request.user, a, b, reussi)

        quiz["temps"].append(duree)
        if reussi:
            quiz["reussites"] += 1
        quiz["index"] += 1
        quiz["debut_question"] = maintenant.isoformat()
        request.session[CLE_SESSION] = quiz

        if quiz["index"] >= NB_QUESTIONS:
            return redirect("revisions:multiplication_resultat")
        return redirect("revisions:multiplication_jouer")

    return render(
        request,
        "revisions/multiplication_jouer.html",
        {"a": a, "b": b, "numero": quiz["index"] + 1, "total": NB_QUESTIONS},
    )


@login_required
def multiplication_resultat(request):
    """Score et temps moyen de réponse, affichés une seule fois (la session est nettoyée)."""
    quiz = request.session.get(CLE_SESSION)
    if not quiz or quiz["index"] < NB_QUESTIONS:
        return redirect("revisions:multiplication_config")
    temps = quiz["temps"]
    temps_moyen = round(sum(temps) / len(temps), 1) if temps else 0
    contexte = {"reussites": quiz["reussites"], "total": NB_QUESTIONS, "temps_moyen": temps_moyen}
    del request.session[CLE_SESSION]
    return render(request, "revisions/multiplication_resultat.html", contexte)


@login_required
def multiplication_statistiques(request):
    """Matrice de réussite (table × table) pour chaque enfant du foyer."""
    tables = range(1, 11)
    enfants = User.objects.filter(is_staff=False, est_parent=False).order_by("ordre", "first_name")
    matrices = []
    for enfant in enfants:
        taux_par_fait = {
            (s.facteur_min, s.facteur_max): s.taux_reussite
            for s in StatistiqueMultiplication.objects.filter(enfant=enfant)
        }
        lignes = []
        for a in tables:
            cellules = []
            for b in tables:
                taux = taux_par_fait.get((min(a, b), max(a, b)))
                cellules.append({"b": b, "taux": taux, "couleur": couleur_pour_taux(taux)})
            lignes.append({"a": a, "cellules": cellules})
        matrices.append({"enfant": enfant, "lignes": lignes})
    return render(
        request,
        "revisions/multiplication_statistiques.html",
        {"matrices": matrices, "tables": tables},
    )
