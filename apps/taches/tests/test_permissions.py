import pytest
from django.urls import reverse

from apps.taches.models import TacheEffectuee, TypeTache


@pytest.fixture
def lecture(db):
    return TypeTache.objects.create(nom="Lecture", points=2)


@pytest.mark.django_db
def test_un_parent_voit_le_formulaire_d_ajout(client, maman):
    client.force_login(maman)
    reponse = client.get(reverse("taches:accueil"))
    assert "Ajouter une tâche faite aujourd'hui" in reponse.content.decode()


@pytest.mark.django_db
def test_un_enfant_ne_voit_pas_le_formulaire_d_ajout(client, philippe):
    client.force_login(philippe)
    reponse = client.get(reverse("taches:accueil"))
    assert "Ajouter une tâche faite aujourd'hui" not in reponse.content.decode()


@pytest.mark.django_db
def test_un_parent_peut_enregistrer_une_tache(client, maman, josephine, lecture):
    client.force_login(maman)
    reponse = client.post(
        reverse("taches:accueil"), {"enfant": josephine.pk, "type_tache": lecture.pk}
    )
    assert reponse.status_code == 302
    tache = TacheEffectuee.objects.get()
    assert tache.enfant == josephine
    assert tache.type_tache == lecture
    assert tache.created_by == maman


@pytest.mark.django_db
def test_un_enfant_ne_peut_pas_enregistrer_une_tache(client, philippe, josephine, lecture):
    client.force_login(philippe)
    reponse = client.post(
        reverse("taches:accueil"), {"enfant": josephine.pk, "type_tache": lecture.pk}
    )
    assert reponse.status_code == 403
    assert not TacheEffectuee.objects.exists()


@pytest.mark.django_db
def test_tout_le_monde_peut_consulter_l_historique(client, philippe):
    client.force_login(philippe)
    assert client.get(reverse("taches:historique")).status_code == 200


@pytest.mark.django_db
def test_tout_le_monde_peut_consulter_le_catalogue(client, philippe):
    client.force_login(philippe)
    assert client.get(reverse("taches:catalogue")).status_code == 200


@pytest.mark.django_db
def test_seul_un_parent_gere_le_catalogue(client, philippe, maman):
    donnees = {"nom": "Rangement", "points": 1, "actif": True}

    client.force_login(philippe)
    reponse = client.post(reverse("taches:catalogue_ajouter"), donnees)
    assert reponse.status_code == 403
    assert not TypeTache.objects.filter(nom="Rangement").exists()

    client.force_login(maman)
    reponse = client.post(reverse("taches:catalogue_ajouter"), donnees)
    assert reponse.status_code == 302
    assert TypeTache.objects.filter(nom="Rangement").exists()


@pytest.mark.django_db
def test_desactiver_une_tache_ne_la_supprime_pas(client, maman, lecture):
    client.force_login(maman)
    reponse = client.post(reverse("taches:catalogue_basculer", args=[lecture.pk]))
    assert reponse.status_code == 302
    lecture.refresh_from_db()
    assert lecture.actif is False


@pytest.mark.django_db
def test_un_parent_peut_supprimer_une_tache_enregistree(client, maman, josephine, lecture):
    tache = TacheEffectuee.objects.create(
        enfant=josephine, type_tache=lecture, date="2026-10-29", created_by=maman
    )
    client.force_login(maman)
    reponse = client.post(reverse("taches:effectuee_supprimer", args=[tache.pk]))
    assert reponse.status_code == 302
    assert not TacheEffectuee.objects.exists()


@pytest.mark.django_db
def test_un_enfant_ne_peut_pas_supprimer_une_tache(client, philippe, josephine, maman, lecture):
    tache = TacheEffectuee.objects.create(
        enfant=josephine, type_tache=lecture, date="2026-10-29", created_by=maman
    )
    client.force_login(philippe)
    reponse = client.post(reverse("taches:effectuee_supprimer", args=[tache.pk]))
    assert reponse.status_code == 403
    assert TacheEffectuee.objects.filter(pk=tache.pk).exists()
