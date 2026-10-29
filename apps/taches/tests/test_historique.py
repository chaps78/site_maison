import pytest
from django.urls import reverse

from apps.taches.models import TacheEffectuee, TypeTache


@pytest.fixture
def lecture(db):
    return TypeTache.objects.create(nom="Lecture", points=2)


@pytest.fixture
def table(db):
    return TypeTache.objects.create(nom="Mettre la table", points=1)


@pytest.mark.django_db
def test_le_total_mensuel_additionne_les_points_et_ignore_les_autres_mois(
    client, maman, philippe, josephine, lecture, table
):
    TacheEffectuee.objects.create(
        enfant=josephine, type_tache=lecture, date="2026-10-05", created_by=maman
    )
    TacheEffectuee.objects.create(
        enfant=josephine, type_tache=table, date="2026-10-12", created_by=maman
    )
    # Mois différent : ne doit pas compter dans le total d'octobre.
    TacheEffectuee.objects.create(
        enfant=philippe, type_tache=table, date="2026-09-30", created_by=maman
    )

    client.force_login(maman)
    reponse = client.get(reverse("taches:historique"), {"annee": 2026, "mois": 10})
    contenu = reponse.content.decode()
    assert "Joséphine</strong> : 3 points" in contenu
    # Philippe n'a rien fait en octobre : il apparaît quand même, avec 0.
    assert "Philippe</strong> : 0 points" in contenu


@pytest.mark.django_db
def test_navigation_mois_precedent_et_suivant_change_d_annee(client, maman):
    client.force_login(maman)
    reponse = client.get(reverse("taches:historique"), {"annee": 2026, "mois": 1})
    contenu = reponse.content.decode()
    assert "annee=2025&mois=12" in contenu  # décembre de l'année précédente
    assert "annee=2026&mois=2" in contenu
