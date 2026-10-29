import pytest
from django.urls import reverse

from apps.core.models import User


@pytest.fixture
def papa(db):
    """Le seul profil administrateur du foyer."""
    papa = User(username="papa", first_name="Papa", ordre=1, est_admin=True)
    papa.set_password("0001")
    papa.save()
    return papa


@pytest.fixture
def maman(db):
    """Un profil ordinaire, pas administrateur."""
    maman = User(username="maman", first_name="Maman", ordre=2)
    maman.set_password("1111")
    maman.save()
    return maman


@pytest.mark.django_db
def test_admin_peut_creer_un_profil(client, papa):
    client.force_login(papa)
    reponse = client.post(
        reverse("core:profil_creer"),
        {"first_name": "Joséphine", "ordre": 4, "code": "4242", "code_confirmation": "4242"},
    )
    assert reponse.status_code == 302
    cree = User.objects.get(username="josephine")
    assert cree.first_name == "Joséphine"
    assert cree.is_staff is False
    assert cree.is_superuser is False
    assert cree.est_admin is False
    assert cree.check_password("4242")


@pytest.mark.django_db
def test_non_admin_ne_peut_pas_creer_un_profil(client, maman):
    client.force_login(maman)
    reponse = client.post(
        reverse("core:profil_creer"),
        {"first_name": "Test", "ordre": 0, "code": "1234", "code_confirmation": "1234"},
    )
    assert reponse.status_code == 403
    assert not User.objects.filter(username="test").exists()


@pytest.mark.django_db
def test_codes_differents_refuses(client, papa):
    client.force_login(papa)
    reponse = client.post(
        reverse("core:profil_creer"),
        {"first_name": "Test", "ordre": 0, "code": "1234", "code_confirmation": "9999"},
    )
    assert reponse.status_code == 200
    assert "ne correspondent pas" in reponse.content.decode()
    assert not User.objects.filter(username="test").exists()


@pytest.mark.django_db
def test_on_peut_changer_son_propre_code(client, maman):
    client.force_login(maman)
    reponse = client.post(
        reverse("core:profil_modifier", args=[maman.pk]),
        {"code": "2222", "code_confirmation": "2222"},
    )
    assert reponse.status_code == 302
    maman.refresh_from_db()
    assert maman.check_password("2222")


@pytest.mark.django_db
def test_on_ne_peut_pas_changer_le_code_de_quelqu_un_d_autre(client, maman, papa):
    client.force_login(maman)
    reponse = client.post(
        reverse("core:profil_modifier", args=[papa.pk]),
        {"code": "9999", "code_confirmation": "9999"},
    )
    assert reponse.status_code == 403
    papa.refresh_from_db()
    assert papa.check_password("0001")  # inchangé


@pytest.mark.django_db
def test_admin_peut_modifier_n_importe_quel_profil(client, papa, maman):
    client.force_login(papa)
    reponse = client.post(
        reverse("core:profil_modifier", args=[maman.pk]),
        {
            "first_name": "Super Maman",
            "ordre": 2,
            "est_admin": False,
            "code": "",
            "code_confirmation": "",
        },
    )
    assert reponse.status_code == 302
    maman.refresh_from_db()
    assert maman.first_name == "Super Maman"
    assert maman.check_password("1111")  # code laissé vide : inchangé


@pytest.mark.django_db
def test_admin_peut_supprimer_un_autre_profil(client, papa, maman):
    client.force_login(papa)
    reponse = client.post(reverse("core:profil_supprimer", args=[maman.pk]))
    assert reponse.status_code == 302
    assert not User.objects.filter(pk=maman.pk).exists()


@pytest.mark.django_db
def test_non_admin_ne_peut_pas_supprimer(client, maman, papa):
    client.force_login(maman)
    reponse = client.post(reverse("core:profil_supprimer", args=[papa.pk]))
    assert reponse.status_code == 403
    assert User.objects.filter(pk=papa.pk).exists()


@pytest.mark.django_db
def test_on_ne_peut_pas_se_supprimer_soi_meme(client, papa):
    client.force_login(papa)
    reponse = client.post(reverse("core:profil_supprimer", args=[papa.pk]))
    assert reponse.status_code == 200
    assert User.objects.filter(pk=papa.pk).exists()


@pytest.mark.django_db
def test_liste_des_profils_exclut_le_compte_d_administration_django(
    client, maman, django_user_model
):
    """Le compte is_staff qui administre /admin/ n'apparaît pas dans ce CRUD."""
    django_user_model.objects.create_user(username="webmaster", password="x", is_staff=True)
    client.force_login(maman)
    reponse = client.get(reverse("core:profils_liste"))
    assert "webmaster" not in reponse.content.decode()
