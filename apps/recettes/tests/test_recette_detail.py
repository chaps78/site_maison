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


@pytest.fixture
def recette(db, user, farine):
    recette = Recette.objects.create(
        titre="Tarte aux pommes", description="Un classique.", created_by=user
    )
    Ingredient.objects.create(recette=recette, type_ingredient=farine, quantite=Decimal("0.3"))
    return recette


def _donnees_formset_modification(lignes, initial, total_extra=3):
    """Données POST pour IngredientFormSetModification (lignes existantes + extra)."""
    total = initial + total_extra
    donnees = {
        "ingredients-TOTAL_FORMS": str(total),
        "ingredients-INITIAL_FORMS": str(initial),
        "ingredients-MIN_NUM_FORMS": "0",
        "ingredients-MAX_NUM_FORMS": "1000",
    }
    for i in range(total):
        valeurs = lignes[i] if i < len(lignes) else {}
        donnees[f"ingredients-{i}-type_ingredient"] = valeurs.get("type_ingredient", "")
        donnees[f"ingredients-{i}-quantite"] = valeurs.get("quantite", "")
        if "id" in valeurs:
            donnees[f"ingredients-{i}-id"] = valeurs["id"]
        if valeurs.get("DELETE"):
            donnees[f"ingredients-{i}-DELETE"] = "on"
    return donnees


@pytest.mark.django_db
def test_le_titre_de_la_liste_mene_au_detail(client, user, recette):
    client.force_login(user)
    reponse = client.get(reverse("recettes:liste"))
    assert reverse("recettes:recette_detail", args=[recette.pk]) in reponse.content.decode()


@pytest.mark.django_db
def test_le_detail_affiche_ingredients_et_commentaire(client, user, recette):
    client.force_login(user)
    reponse = client.get(reverse("recettes:recette_detail", args=[recette.pk]))
    contenu = reponse.content.decode()
    assert reponse.status_code == 200
    assert "Farine" in contenu
    assert "Un classique." in contenu
    assert reverse("recettes:recette_modifier", args=[recette.pk]) in contenu


@pytest.mark.django_db
def test_le_formulaire_de_modification_inclut_l_id_des_lignes_existantes(client, user, recette):
    """Régression : sans le champ caché id, Django ne reconnaît pas les lignes
    existantes et « Enregistrer » ne modifiait rien (voir recette_form.html)."""
    client.force_login(user)
    ingredient = recette.ingredients.get()
    reponse = client.get(reverse("recettes:recette_modifier", args=[recette.pk]))
    attendu = f'name="ingredients-0-id" value="{ingredient.pk}"'
    assert attendu in reponse.content.decode()


@pytest.mark.django_db
def test_modifier_le_titre_et_le_commentaire(client, user, recette, farine):
    client.force_login(user)
    ingredient = recette.ingredients.get()
    donnees = {"titre": "Tarte aux pommes (maison)", "description": "Encore meilleure."}
    donnees.update(
        _donnees_formset_modification(
            [{"id": ingredient.pk, "type_ingredient": farine.pk, "quantite": "0.3"}],
            initial=1,
        )
    )

    reponse = client.post(reverse("recettes:recette_modifier", args=[recette.pk]), donnees)

    assert reponse.status_code == 302
    recette.refresh_from_db()
    assert recette.titre == "Tarte aux pommes (maison)"
    assert recette.description == "Encore meilleure."


@pytest.mark.django_db
def test_ajouter_un_ingredient_en_modifiant(client, user, recette, farine, pommes):
    client.force_login(user)
    ingredient = recette.ingredients.get()
    donnees = {"titre": recette.titre, "description": recette.description}
    donnees.update(
        _donnees_formset_modification(
            [
                {"id": ingredient.pk, "type_ingredient": farine.pk, "quantite": "0.3"},
                {"type_ingredient": pommes.pk, "quantite": "4"},
            ],
            initial=1,
        )
    )

    client.post(reverse("recettes:recette_modifier", args=[recette.pk]), donnees)

    assert recette.ingredients.count() == 2


@pytest.mark.django_db
def test_retirer_un_ingredient_en_modifiant(client, user, recette, farine):
    client.force_login(user)
    ingredient = recette.ingredients.get()
    donnees = {"titre": recette.titre, "description": recette.description}
    donnees.update(
        _donnees_formset_modification(
            [
                {
                    "id": ingredient.pk,
                    "type_ingredient": farine.pk,
                    "quantite": "0.3",
                    "DELETE": True,
                }
            ],
            initial=1,
        )
    )

    client.post(reverse("recettes:recette_modifier", args=[recette.pk]), donnees)

    assert recette.ingredients.count() == 0
