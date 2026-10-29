from decimal import Decimal

import pytest
from django.urls import reverse

from apps.recettes.models import Ingredient, Recette, TypeIngredient


@pytest.fixture
def farine(db):
    return TypeIngredient.objects.create(
        nom="Farine", quantification=TypeIngredient.Quantification.KILOGRAMME
    )


@pytest.fixture
def pommes(db):
    return TypeIngredient.objects.create(
        nom="Pommes", quantification=TypeIngredient.Quantification.QUANTITE
    )


def _donnees_formset(lignes, total=10):
    """Construit les données POST du formset (management form + lignes, le reste vide)."""
    donnees = {
        "ingredients-TOTAL_FORMS": str(total),
        "ingredients-INITIAL_FORMS": "0",
        "ingredients-MIN_NUM_FORMS": "0",
        "ingredients-MAX_NUM_FORMS": "1000",
    }
    for i in range(total):
        type_ingredient, quantite = lignes[i] if i < len(lignes) else ("", "")
        donnees[f"ingredients-{i}-type_ingredient"] = type_ingredient
        donnees[f"ingredients-{i}-quantite"] = quantite
    return donnees


@pytest.mark.django_db
def test_creer_une_recette_avec_des_ingredients(client, user, farine, pommes):
    client.force_login(user)
    donnees = {"titre": "Tarte aux pommes", "description": "Un classique."}
    donnees.update(_donnees_formset([(farine.pk, "0.2"), (pommes.pk, "4")]))

    reponse = client.post(reverse("recettes:recette_creer"), donnees)

    assert reponse.status_code == 302
    recette = Recette.objects.get(titre="Tarte aux pommes")
    assert recette.created_by == user
    assert recette.description == "Un classique."
    ingredients = {i.type_ingredient.nom: i.quantite for i in recette.ingredients.all()}
    assert ingredients == {"Farine": Decimal("0.20"), "Pommes": Decimal("4.00")}


@pytest.mark.django_db
def test_les_lignes_vides_sont_ignorees(client, user, farine):
    client.force_login(user)
    donnees = {"titre": "Pain", "description": ""}
    donnees.update(_donnees_formset([(farine.pk, "0.5")]))  # 9 lignes vides derrière

    client.post(reverse("recettes:recette_creer"), donnees)

    recette = Recette.objects.get(titre="Pain")
    assert recette.ingredients.count() == 1


@pytest.mark.django_db
def test_le_titre_apparait_dans_la_liste(client, user, farine):
    Recette.objects.create(titre="Soupe", created_by=user)
    client.force_login(user)
    reponse = client.get(reverse("recettes:liste"))
    assert "Soupe" in reponse.content.decode()


@pytest.mark.django_db
def test_quantite_sans_ingredient_est_refusee(client, user, farine):
    """Une ligne avec une quantité mais sans ingrédient choisi doit être signalée."""
    client.force_login(user)
    donnees = {"titre": "Test", "description": ""}
    donnees.update(_donnees_formset([("", "2")]))

    reponse = client.post(reverse("recettes:recette_creer"), donnees)

    assert reponse.status_code == 200
    assert not Recette.objects.filter(titre="Test").exists()


@pytest.mark.django_db
def test_supprimer_un_ingredient_utilise_affiche_un_message(client, user, farine):
    recette = Recette.objects.create(titre="Pain", created_by=user)
    Ingredient.objects.create(recette=recette, type_ingredient=farine)
    client.force_login(user)

    reponse = client.post(reverse("recettes:type_ingredient_supprimer", args=[farine.pk]))

    assert reponse.status_code == 200
    assert "impossible de le supprimer" in reponse.content.decode()
    assert TypeIngredient.objects.filter(pk=farine.pk).exists()
