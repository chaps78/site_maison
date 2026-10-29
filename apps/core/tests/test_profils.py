import pytest
from django.urls import reverse

from apps.core.models import User


@pytest.fixture
def profil(db):
    profil = User(username="maman", first_name="Maman", ordre=2)
    profil.set_password("1111")
    profil.save()
    return profil


@pytest.mark.django_db
def test_creer_un_profil(client, profil):
    client.force_login(profil)
    reponse = client.post(
        reverse("core:profil_creer"),
        {"first_name": "Joséphine", "ordre": 4, "code": "4242", "code_confirmation": "4242"},
    )
    assert reponse.status_code == 302
    cree = User.objects.get(username="josephine")
    assert cree.first_name == "Joséphine"
    assert cree.is_staff is False
    assert cree.is_superuser is False
    assert cree.check_password("4242")


@pytest.mark.django_db
def test_codes_differents_refuses(client, profil):
    client.force_login(profil)
    reponse = client.post(
        reverse("core:profil_creer"),
        {"first_name": "Test", "ordre": 0, "code": "1234", "code_confirmation": "9999"},
    )
    assert reponse.status_code == 200
    assert "ne correspondent pas" in reponse.content.decode()
    assert not User.objects.filter(username="test").exists()


@pytest.mark.django_db
def test_modifier_un_profil_sans_changer_le_code(client, profil):
    client.force_login(profil)
    reponse = client.post(
        reverse("core:profil_modifier", args=[profil.pk]),
        {"first_name": "Super Maman", "ordre": 2, "code": "", "code_confirmation": ""},
    )
    assert reponse.status_code == 302
    profil.refresh_from_db()
    assert profil.first_name == "Super Maman"
    assert profil.check_password("1111")  # inchangé


@pytest.mark.django_db
def test_supprimer_un_autre_profil(client, profil):
    autre = User(username="papa", first_name="Papa", ordre=1)
    autre.set_password("0001")
    autre.save()
    client.force_login(profil)
    reponse = client.post(reverse("core:profil_supprimer", args=[autre.pk]))
    assert reponse.status_code == 302
    assert not User.objects.filter(pk=autre.pk).exists()


@pytest.mark.django_db
def test_on_ne_peut_pas_se_supprimer_soi_meme(client, profil):
    client.force_login(profil)
    reponse = client.post(reverse("core:profil_supprimer", args=[profil.pk]))
    assert reponse.status_code == 200
    assert User.objects.filter(pk=profil.pk).exists()


@pytest.mark.django_db
def test_liste_des_profils_exclut_le_compte_admin(client, profil, django_user_model):
    django_user_model.objects.create_user(username="admin", password="x", is_staff=True)
    client.force_login(profil)
    reponse = client.get(reverse("core:profils_liste"))
    assert "admin" not in reponse.content.decode()
