from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from apps.calendrier.models import Evenement

BUENOS_AIRES = ZoneInfo("America/Argentina/Buenos_Aires")


def _evenement(**kwargs):
    valeurs = {
        "titre": "Réunion",
        "debut": datetime(2026, 5, 1, 10, 0, tzinfo=BUENOS_AIRES),
        "fin": datetime(2026, 5, 1, 11, 0, tzinfo=BUENOS_AIRES),
    }
    return Evenement(**{**valeurs, **kwargs})


@pytest.mark.django_db
def test_valeurs_par_defaut():
    evenement = _evenement()
    evenement.save()
    assert evenement.categorie == Evenement.Categorie.AUTRE
    assert evenement.journee_entiere is False
    assert str(evenement) == "Réunion"


@pytest.mark.django_db
def test_rrule_est_reserve_et_vide_en_v1():
    evenement = _evenement()
    evenement.save()
    evenement.refresh_from_db()
    assert evenement.rrule is None


@pytest.mark.django_db
def test_la_fin_ne_peut_pas_preceder_le_debut():
    evenement = _evenement(fin=datetime(2026, 5, 1, 9, 0, tzinfo=BUENOS_AIRES))
    with pytest.raises(ValidationError) as erreur:
        evenement.full_clean()
    assert "La fin ne peut pas précéder le début." in str(erreur.value)


@pytest.mark.django_db
def test_fin_egale_au_debut_est_acceptee():
    instant = datetime(2026, 5, 1, 10, 0, tzinfo=BUENOS_AIRES)
    _evenement(debut=instant, fin=instant).full_clean()


@pytest.mark.django_db
def test_ordre_chronologique():
    tard = _evenement(titre="Tard", debut=datetime(2026, 5, 2, 8, 0, tzinfo=BUENOS_AIRES))
    tot = _evenement(titre="Tôt", debut=datetime(2026, 5, 1, 8, 0, tzinfo=BUENOS_AIRES))
    tard.fin = datetime(2026, 5, 2, 9, 0, tzinfo=BUENOS_AIRES)
    tot.fin = datetime(2026, 5, 1, 9, 0, tzinfo=BUENOS_AIRES)
    tard.save()
    tot.save()
    assert [e.titre for e in Evenement.objects.all()] == ["Tôt", "Tard"]
