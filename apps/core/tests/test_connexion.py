import pytest
from django.urls import reverse

from apps.core.models import User


@pytest.fixture
def profil(db):
    """Un profil du foyer (pas un compte d'administration) avec le code 1234."""
    profil = User(username="philippe", first_name="Philippe", ordre=3)
    profil.set_password("1234")
    profil.save()
    return profil


@pytest.mark.django_db
def test_accueil_redirige_vers_la_connexion_si_anonyme(client):
    reponse = client.get(reverse("core:accueil"))
    assert reponse.status_code == 302
    assert reponse.url == f"{reverse('core:connexion')}?next={reverse('core:accueil')}"


@pytest.mark.django_db
def test_ecran_de_connexion_liste_les_profils_non_staff_seulement(client, profil, django_user_model):
    django_user_model.objects.create_user(username="admin", password="x", is_staff=True)
    reponse = client.get(reverse("core:connexion"))
    assert reponse.status_code == 200
    assert "Philippe" in reponse.content.decode()
    assert "admin" not in reponse.content.decode()


@pytest.mark.django_db
def test_bon_code_connecte_et_redirige_vers_l_accueil(client, profil):
    reponse = client.post(
        reverse("core:connexion_code", args=[profil.username]), {"code": "1234"}
    )
    assert reponse.status_code == 302
    assert reponse.url == reverse("core:accueil")
    # La session est bien ouverte : la page d'accueil est maintenant accessible.
    assert client.get(reverse("core:accueil")).status_code == 200


@pytest.mark.django_db
def test_mauvais_code_n_authentifie_pas(client, profil):
    reponse = client.post(
        reverse("core:connexion_code", args=[profil.username]), {"code": "0000"}
    )
    assert reponse.status_code == 200
    assert "Code incorrect" in reponse.content.decode()
    assert client.get(reverse("core:accueil")).status_code == 302


@pytest.mark.django_db
def test_deconnexion_coupe_la_session(client, profil):
    client.post(reverse("core:connexion_code", args=[profil.username]), {"code": "1234"})
    reponse = client.post(reverse("core:deconnexion"))
    assert reponse.status_code == 302
    assert client.get(reverse("core:accueil")).status_code == 302
