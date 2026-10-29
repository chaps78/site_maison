"""Fixtures partagées par tous les tests."""

import pytest

from apps.core.models import User


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(username="alice", password="motdepasse-test")


@pytest.fixture
def client_connecte(client, user):
    client.force_login(user)
    return client


def _creer_profil(username, prenom, code, ordre, est_admin=False, est_parent=False):
    """Un profil du foyer (core.User, is_staff=False) avec un code à 4 chiffres."""
    profil = User(
        username=username,
        first_name=prenom,
        ordre=ordre,
        est_admin=est_admin,
        est_parent=est_parent,
    )
    profil.set_password(code)
    profil.save()
    return profil


@pytest.fixture
def papa(db):
    """Parent et administrateur du foyer (seul à gérer /profils/)."""
    return _creer_profil("papa", "Papa", "0001", 1, est_admin=True, est_parent=True)


@pytest.fixture
def maman(db):
    """Parent, sans le statut administrateur de /profils/."""
    return _creer_profil("maman", "Maman", "1111", 2, est_parent=True)


@pytest.fixture
def philippe(db):
    """Enfant : consultation seulement, ne peut changer que son propre code."""
    return _creer_profil("philippe", "Philippe", "2222", 3)


@pytest.fixture
def josephine(db):
    """Enfant : consultation seulement, ne peut changer que son propre code."""
    return _creer_profil("josephine", "Joséphine", "3333", 4)
