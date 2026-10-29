import pytest
from django.urls import reverse

from apps.recettes.models import TypeIngredient


@pytest.fixture
def farine(db):
    return TypeIngredient.objects.create(
        nom="Farine", quantification=TypeIngredient.Quantification.KILOGRAMME
    )


@pytest.mark.django_db
def test_la_liste_affiche_le_catalogue(client, user, farine):
    client.force_login(user)
    reponse = client.get(reverse("recettes:types_ingredients_liste"))
    assert reponse.status_code == 200
    assert "Farine" in reponse.content.decode()


@pytest.mark.django_db
def test_creer_un_type_ingredient(client, user):
    client.force_login(user)
    reponse = client.post(
        reverse("recettes:type_ingredient_creer"),
        {"nom": "Lait", "quantification": TypeIngredient.Quantification.LITRE},
    )
    assert reponse.status_code == 302
    assert TypeIngredient.objects.filter(nom="Lait").exists()


@pytest.mark.django_db
def test_modifier_un_type_ingredient(client, user, farine):
    client.force_login(user)
    reponse = client.post(
        reverse("recettes:type_ingredient_modifier", args=[farine.pk]),
        {"nom": "Farine de blé", "quantification": TypeIngredient.Quantification.KILOGRAMME},
    )
    assert reponse.status_code == 302
    farine.refresh_from_db()
    assert farine.nom == "Farine de blé"


@pytest.mark.django_db
def test_supprimer_un_type_ingredient(client, user, farine):
    client.force_login(user)
    reponse = client.post(reverse("recettes:type_ingredient_supprimer", args=[farine.pk]))
    assert reponse.status_code == 302
    assert not TypeIngredient.objects.filter(pk=farine.pk).exists()
