from django.conf import settings
from django.db import models

from apps.recettes.models import Ingredient, Recette

# 1er choix = 3 points, 2e = 2 points, 3e = 1 point.
POINTS_PAR_RANG = {1: 3, 2: 2, 3: 1}


class Vote(models.Model):
    """Les choix d'une personne pour le dîner d'un jour donné (1 à 3 plats classés).

    SET_NULL sur les recettes (pas CASCADE) : si une recette est supprimée, on ne veut
    perdre que ce choix-là, pas tout le vote de la personne (ses 2 autres choix restent).
    """

    votant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes_diner"
    )
    date = models.DateField()
    premier_choix = models.ForeignKey(
        Recette, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    deuxieme_choix = models.ForeignKey(
        Recette, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    troisieme_choix = models.ForeignKey(
        Recette, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["votant", "date"], name="un_vote_par_personne_et_par_jour"
            )
        ]

    def __str__(self):
        return f"{self.votant} – {self.date}"

    @property
    def choix_classes(self):
        """[(rang, recette, points), ...] pour les choix réellement remplis."""
        return [
            (rang, recette, POINTS_PAR_RANG[rang])
            for rang, recette in (
                (1, self.premier_choix),
                (2, self.deuxieme_choix),
                (3, self.troisieme_choix),
            )
            if recette is not None
        ]


class EtatCourses(models.Model):
    """Pour un plat proposé un jour donné : faut-il faire des courses, et quels
    ingrédients manquent. Partagé par tout le foyer (pas de notion de « qui a coché »).
    """

    recette = models.ForeignKey(Recette, on_delete=models.CASCADE, related_name="etats_courses")
    date = models.DateField()
    courses_a_faire = models.BooleanField("courses à faire", default=False)
    ingredients_manquants = models.ManyToManyField(
        Ingredient, blank=True, related_name="etats_courses_manquants"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recette", "date"], name="un_etat_courses_par_plat_et_par_jour"
            )
        ]

    def __str__(self):
        return f"{self.recette} – {self.date}"
