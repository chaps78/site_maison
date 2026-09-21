"""Fixtures partagées par tous les tests."""

import pytest


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(username="alice", password="motdepasse-test")


@pytest.fixture
def client_connecte(client, user):
    client.force_login(user)
    return client
