from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Compte d'un membre du foyer.

    Volontairement vide : changer de modèle utilisateur après la première migration est
    très pénible, alors qu'en partir d'un modèle à nous permet d'ajouter des champs plus tard.
    """

    # Ordre d'affichage des boutons sur l'écran de connexion et dans la liste des profils
    # (is_staff=False distingue les profils du foyer du ou des comptes d'administration Django).
    ordre = models.PositiveSmallIntegerField("ordre d'affichage", default=0)


class Traced(models.Model):
    """Base des contenus partagés : le foyer voit tout, on trace juste qui a créé quoi."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # effacer un compte n'efface pas ses données
        null=True,
        blank=True,
        editable=False,  # renseigné par les vues et par l'admin, jamais saisi
        related_name="%(app_label)s_%(class)s_created",
        verbose_name="créé par",
    )
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    class Meta:
        abstract = True
