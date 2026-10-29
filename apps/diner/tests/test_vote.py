import pytest
from django.urls import reverse
from django.utils import timezone

from apps.diner.models import EtatCourses, Vote
from apps.recettes.models import Ingredient, Recette, TypeIngredient


@pytest.fixture
def tarte(db):
    return Recette.objects.create(titre="Tarte aux pommes")


@pytest.fixture
def soupe(db):
    return Recette.objects.create(titre="Soupe")


@pytest.fixture
def pates(db):
    return Recette.objects.create(titre="Pâtes")


@pytest.mark.django_db
def test_voter_cree_un_vote_du_jour(client, maman, tarte, soupe):
    client.force_login(maman)
    reponse = client.post(
        reverse("diner:accueil"),
        {
            "premier_choix": tarte.pk,
            "deuxieme_choix": soupe.pk,
            "troisieme_choix": "",
        },
    )
    assert reponse.status_code == 302
    vote = Vote.objects.get(votant=maman)
    assert vote.premier_choix == tarte
    assert vote.deuxieme_choix == soupe
    assert vote.troisieme_choix is None


@pytest.mark.django_db
def test_revoter_remplace_le_vote_precedent(client, maman, tarte, soupe):
    client.force_login(maman)
    client.post(reverse("diner:accueil"), {"premier_choix": tarte.pk})
    client.post(reverse("diner:accueil"), {"premier_choix": soupe.pk})
    assert Vote.objects.filter(votant=maman).count() == 1
    assert Vote.objects.get(votant=maman).premier_choix == soupe


@pytest.mark.django_db
def test_trois_choix_identiques_refuses(client, maman, tarte):
    client.force_login(maman)
    reponse = client.post(
        reverse("diner:accueil"),
        {"premier_choix": tarte.pk, "deuxieme_choix": tarte.pk},
    )
    assert reponse.status_code == 200
    assert not Vote.objects.filter(votant=maman).exists()


@pytest.mark.django_db
def test_le_premier_choix_est_obligatoire(client, maman):
    client.force_login(maman)
    reponse = client.post(reverse("diner:accueil"), {})
    assert reponse.status_code == 200
    assert not Vote.objects.filter(votant=maman).exists()


def _aujourdhui():
    return timezone.localdate()


@pytest.mark.django_db
def test_les_points_s_additionnent_entre_votants(client, maman, papa, philippe, tarte, soupe):
    Vote.objects.create(votant=papa, date=_aujourdhui(), premier_choix=tarte)
    Vote.objects.create(
        votant=philippe, date=_aujourdhui(), premier_choix=soupe, deuxieme_choix=tarte
    )

    client.force_login(maman)
    reponse = client.get(reverse("diner:accueil"))
    contenu = reponse.content.decode()

    # Tarte : 3 (papa, 1er) + 2 (philippe, 2e) = 5 points. Soupe : 3 points.
    assert "Tarte aux pommes</strong> — 5 points" in contenu
    assert "Soupe</strong> — 3 points" in contenu


@pytest.mark.django_db
def test_on_voit_qui_a_vote_pour_quel_plat(client, maman, papa, tarte):
    Vote.objects.create(votant=papa, date=_aujourdhui(), premier_choix=tarte)
    client.force_login(maman)
    reponse = client.get(reverse("diner:accueil"))
    assert "Papa" in reponse.content.decode()


@pytest.mark.django_db
def test_basculer_courses_a_faire(client, maman, papa, tarte):
    Vote.objects.create(votant=papa, date=_aujourdhui(), premier_choix=tarte)
    client.force_login(maman)

    reponse = client.post(reverse("diner:courses_basculer", args=[tarte.pk]))

    assert reponse.status_code == 302
    etat = EtatCourses.objects.get(recette=tarte, date=_aujourdhui())
    assert etat.courses_a_faire is True


@pytest.mark.django_db
def test_marquer_des_ingredients_manquants(client, maman, papa, tarte):
    farine = TypeIngredient.objects.create(
        nom="Farine", quantification=TypeIngredient.Quantification.KILOGRAMME
    )
    ingredient = Ingredient.objects.create(recette=tarte, type_ingredient=farine)
    Vote.objects.create(votant=papa, date=_aujourdhui(), premier_choix=tarte)
    client.force_login(maman)

    reponse = client.post(
        reverse("diner:ingredients_manquants_modifier", args=[tarte.pk]),
        {"manquant": [ingredient.pk]},
    )

    assert reponse.status_code == 302
    etat = EtatCourses.objects.get(recette=tarte, date=_aujourdhui())
    assert list(etat.ingredients_manquants.all()) == [ingredient]
