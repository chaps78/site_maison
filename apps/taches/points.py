"""Calcul des totaux de points par enfant, réutilisé par la vue historique et par le menu."""

from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from apps.core.models import User


def totaux_du_mois(annee, mois):
    """Un enfant par ligne, avec son total de points pour ce mois (0 s'il n'a rien fait)."""
    return (
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
