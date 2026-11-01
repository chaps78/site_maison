import pytest
from django.urls import reverse

from apps.taches.models import TacheEffectuee, TypeTache
from apps.taches.points import totaux_du_mois


@pytest.mark.django_db
def test_un_parent_peut_creer_une_punition_a_points_negatifs(client, maman):
    client.force_login(maman)
    reponse = client.post(
        reverse("taches:catalogue_ajouter"),
        {"nom": "A tapé sa sœur", "points": -5, "actif": True},
    )
    assert reponse.status_code == 302
    punition = TypeTache.objects.get(nom="A tapé sa sœur")
    assert punition.points == -5


@pytest.mark.django_db
def test_une_punition_retire_des_points_au_total_du_mois(maman, philippe):
    lecture = TypeTache.objects.create(nom="Lecture", points=2)
    punition = TypeTache.objects.create(nom="Punition", points=-5)
    TacheEffectuee.objects.create(
        enfant=philippe, type_tache=lecture, date="2026-11-01", created_by=maman
    )
    TacheEffectuee.objects.create(
        enfant=philippe, type_tache=punition, date="2026-11-01", created_by=maman
    )

    totaux = {e.pk: e.total for e in totaux_du_mois(2026, 11)}

    assert totaux[philippe.pk] == -3


@pytest.mark.django_db
def test_la_punition_est_signalee_dans_le_catalogue(client, maman):
    TypeTache.objects.create(nom="Punition", points=-5)
    client.force_login(maman)
    reponse = client.get(reverse("taches:catalogue"))
    contenu = reponse.content.decode()
    assert "punition" in contenu
    assert "-5 point" in contenu
