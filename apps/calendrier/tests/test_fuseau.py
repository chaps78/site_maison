"""Fuseaux horaires : stockage en UTC, affichage à l'heure de Buenos Aires.

Buenos Aires est en UTC-3 toute l'année (pas d'heure d'été). L'événement de référence est
choisi à 23h30 locale : en UTC il tombe le lendemain à 02h30, ce qui fait apparaître les
erreurs de fuseau (mauvais jour) que des heures « en plein jour » masqueraient.
"""

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest
from django.conf import settings
from django.db import connection
from django.template import Context, Template
from django.utils import timezone

from apps.calendrier.models import Evenement

BUENOS_AIRES = ZoneInfo("America/Argentina/Buenos_Aires")


@pytest.fixture
def evenement(db):
    """Le 15 mars 2026 de 23h30 à 23h59 heure de Buenos Aires (= 16 mars 02h30-02h59 UTC)."""
    return Evenement.objects.create(
        titre="Diner tardif",
        debut=datetime(2026, 3, 15, 23, 30, tzinfo=BUENOS_AIRES),
        fin=datetime(2026, 3, 15, 23, 59, tzinfo=BUENOS_AIRES),
    )


def test_configuration_du_fuseau():
    assert settings.TIME_ZONE == "America/Argentina/Buenos_Aires"
    assert settings.USE_TZ is True
    assert timezone.get_current_timezone_name() == "America/Argentina/Buenos_Aires"


def test_la_base_stocke_en_utc(evenement):
    """La valeur brute en base (sans passer par l'ORM) est en UTC."""
    with connection.cursor() as curseur:
        curseur.execute("SELECT debut FROM calendrier_evenement WHERE id = %s", [evenement.pk])
        (brut,) = curseur.fetchone()
    assert str(brut).startswith("2026-03-16 02:30:00")


def test_lu_depuis_la_base_c_est_de_l_utc(evenement):
    evenement.refresh_from_db()
    assert evenement.debut.utcoffset().total_seconds() == 0
    assert evenement.debut == datetime(2026, 3, 16, 2, 30, tzinfo=UTC)


def test_localtime_donne_l_heure_de_buenos_aires(evenement):
    evenement.refresh_from_db()
    local = timezone.localtime(evenement.debut)
    assert (local.year, local.month, local.day) == (2026, 3, 15)  # veille en UTC
    assert (local.hour, local.minute) == (23, 30)


def test_un_template_affiche_l_heure_locale(evenement):
    evenement.refresh_from_db()
    template = Template('{{ e.debut|date:"d/m/Y H:i" }}')
    assert template.render(Context({"e": evenement})) == "15/03/2026 23:30"


def test_filtre_par_jour_local(evenement):
    """`debut__date` compare au jour local : l'événement est le 15, pas le 16 (jour UTC)."""
    assert Evenement.objects.filter(debut__date=date(2026, 3, 15)).count() == 1
    assert Evenement.objects.filter(debut__date=date(2026, 3, 16)).count() == 0


def test_isoformat_conserve_le_decalage(evenement):
    """Base de la vue JSON pour FullCalendar : un datetime aware sérialise son décalage."""
    evenement.refresh_from_db()
    assert evenement.debut.isoformat() == "2026-03-16T02:30:00+00:00"
    assert timezone.localtime(evenement.debut).isoformat() == "2026-03-15T23:30:00-03:00"
