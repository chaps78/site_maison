"""Context processor : expose le total de points du mois en cours au menu (core/base.html).

Enregistré dans config/settings.py (TEMPLATES) ; une requête supplémentaire par page, mais
le foyer est petit et la vue elle-même ne fait rien de plus coûteux qu'un COUNT/SUM groupé.
"""

from django.utils import timezone

from .points import totaux_du_mois


def points_du_mois(request):
    if not request.user.is_authenticated:
        return {}
    aujourdhui = timezone.localdate()
    return {"points_du_mois": totaux_du_mois(aujourdhui.year, aujourdhui.month)}
