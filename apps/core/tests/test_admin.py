import pytest
from django.contrib import admin
from django.urls import reverse

from apps.recettes.admin import RecetteAdmin
from apps.recettes.models import Recette

PAGES_ADMIN = [
    "core_user",
    "recettes_recette",
    "recettes_tag",
    "calendrier_evenement",
]


@pytest.mark.django_db
@pytest.mark.parametrize("modele", PAGES_ADMIN)
def test_pages_admin_accessibles(admin_client, modele):
    """Liste et formulaire d'ajout s'affichent sans erreur (modèles et admin bien câblés)."""
    assert admin_client.get(reverse(f"admin:{modele}_changelist")).status_code == 200
    assert admin_client.get(reverse(f"admin:{modele}_add")).status_code == 200


@pytest.mark.django_db
def test_l_admin_renseigne_created_by_a_la_creation(rf, user):
    request = rf.post("/")
    request.user = user
    recette = Recette(titre="Crêpes", instructions="Mélanger.")
    RecetteAdmin(Recette, admin.site).save_model(request, recette, form=None, change=False)
    recette.refresh_from_db()
    assert recette.created_by == user


@pytest.mark.django_db
def test_l_admin_ne_change_pas_l_auteur_a_la_modification(rf, user, django_user_model):
    autre = django_user_model.objects.create_user(username="bob", password="x")
    recette = Recette.objects.create(titre="Crêpes", instructions="Mélanger.", created_by=user)
    request = rf.post("/")
    request.user = autre
    RecetteAdmin(Recette, admin.site).save_model(request, recette, form=None, change=True)
    recette.refresh_from_db()
    assert recette.created_by == user
