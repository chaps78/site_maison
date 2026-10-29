import pytest
from django.urls import reverse

from apps.revisions.models import ResultatAccentuation


@pytest.mark.django_db
def test_la_page_de_jeu_s_affiche(client, philippe):
    client.force_login(philippe)
    reponse = client.get(reverse("revisions:accentuation_jouer"))
    assert reponse.status_code == 200
    assert "RUTA_GUARDAR" in reponse.content.decode()


@pytest.mark.django_db
def test_enregistrer_un_resultat(client, philippe):
    client.force_login(philippe)
    reponse = client.post(reverse("revisions:accentuation_enregistrer"), {"score": 8, "total": 10})
    assert reponse.status_code == 200
    resultat = ResultatAccentuation.objects.get()
    assert resultat.created_by == philippe
    assert resultat.score == 8
    assert resultat.total == 10


@pytest.mark.django_db
def test_enregistrer_refuse_des_valeurs_invalides(client, philippe):
    client.force_login(philippe)
    reponse = client.post(
        reverse("revisions:accentuation_enregistrer"), {"score": "oups", "total": 10}
    )
    assert reponse.status_code == 400
    assert not ResultatAccentuation.objects.exists()


@pytest.mark.django_db
def test_un_parent_voit_la_moyenne(client, maman, philippe):
    ResultatAccentuation.objects.create(created_by=philippe, score=8, total=10)
    ResultatAccentuation.objects.create(created_by=philippe, score=6, total=10)
    client.force_login(maman)
    reponse = client.get(reverse("revisions:accentuation_statistiques"))
    assert reponse.status_code == 200
    assert "70%" in reponse.content.decode()  # moyenne de 80% et 60%


@pytest.mark.django_db
def test_un_enfant_ne_voit_pas_les_statistiques(client, philippe):
    client.force_login(philippe)
    reponse = client.get(reverse("revisions:accentuation_statistiques"))
    assert reponse.status_code == 403
