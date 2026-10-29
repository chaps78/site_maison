from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from apps.recettes.models import Ingredient, Recette, Tag, TypeIngredient


@pytest.fixture
def recette(db, user):
    return Recette.objects.create(
        titre="Tarte aux pommes", instructions="Étaler la pâte.", created_by=user
    )


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


def test_valeurs_par_defaut(recette):
    assert recette.portions == 4
    assert recette.favori is False
    assert str(recette) == "Tarte aux pommes"


def test_les_ingredients_suivent_le_champ_ordre(recette, farine, pommes):
    sucre = TypeIngredient.objects.create(
        nom="Sucre", quantification=TypeIngredient.Quantification.GRAMME
    )
    Ingredient.objects.create(recette=recette, type_ingredient=sucre, ordre=2)
    Ingredient.objects.create(recette=recette, type_ingredient=pommes, ordre=1)
    Ingredient.objects.create(recette=recette, type_ingredient=farine, ordre=3)
    noms = [i.type_ingredient.nom for i in recette.ingredients.all()]
    assert noms == ["Pommes", "Sucre", "Farine"]


def test_quantite_decimale_et_facultative(recette, farine):
    ingredient = Ingredient.objects.create(recette=recette, type_ingredient=farine)
    assert ingredient.quantite is None
    ingredient.quantite = Decimal("1.50")
    ingredient.full_clean()


def test_on_ne_peut_pas_supprimer_un_ingredient_utilise_dans_une_recette(recette, farine):
    Ingredient.objects.create(recette=recette, type_ingredient=farine)
    with pytest.raises(ProtectedError):
        farine.delete()


def test_supprimer_la_recette_supprime_ses_ingredients(recette, pommes):
    Ingredient.objects.create(recette=recette, type_ingredient=pommes)
    recette.delete()
    assert Ingredient.objects.count() == 0


def test_le_slug_d_un_tag_est_unique(db):
    Tag.objects.create(nom="Dessert", slug="dessert")
    with pytest.raises(IntegrityError), transaction.atomic():
        Tag.objects.create(nom="Desserts", slug="dessert")


def test_filtre_par_tag(recette):
    dessert = Tag.objects.create(nom="Dessert", slug="dessert")
    recette.tags.add(dessert)
    Recette.objects.create(titre="Soupe", instructions="Mixer.")
    assert list(Recette.objects.filter(tags__slug="dessert")) == [recette]


def test_supprimer_l_auteur_conserve_la_recette(recette, user):
    user.delete()
    recette.refresh_from_db()
    assert recette.created_by is None


def test_le_nom_d_un_type_ingredient_est_unique(db):
    TypeIngredient.objects.create(
        nom="Farine", quantification=TypeIngredient.Quantification.KILOGRAMME
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        TypeIngredient.objects.create(
            nom="Farine", quantification=TypeIngredient.Quantification.LITRE
        )


def test_str_type_ingredient(db):
    type_ingredient = TypeIngredient.objects.create(
        nom="Lait", quantification=TypeIngredient.Quantification.LITRE
    )
    assert str(type_ingredient) == "Lait"
