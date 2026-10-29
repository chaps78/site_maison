"""La date enregistrée doit être le jour local (Buenos Aires), jamais le jour UTC.

Même principe que apps/calendrier/tests/test_fuseau.py : on choisit un instant où le jour
UTC et le jour local diffèrent pour faire apparaître une éventuelle erreur de fuseau.
"""

from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.taches.models import TacheEffectuee, TypeTache


@pytest.mark.django_db
def test_la_date_enregistree_est_le_jour_local_pas_le_jour_utc(client, maman, josephine):
    tache_type = TypeTache.objects.create(nom="Lecture", points=2)
    # 1h du matin UTC le 16 mars = 22h le 15 mars à Buenos Aires (UTC-3, pas d'heure d'été).
    instant = datetime(2026, 3, 16, 1, 0, tzinfo=UTC)

    client.force_login(maman)
    with patch("django.utils.timezone.now", return_value=instant):
        reponse = client.post(
            reverse("taches:accueil"), {"enfant": josephine.pk, "type_tache": tache_type.pk}
        )

    assert reponse.status_code == 302
    tache = TacheEffectuee.objects.get()
    assert tache.date.isoformat() == "2026-03-15"  # jour local, pas le 16 (jour UTC)
