from django.conf import settings
from django.db import models


class StatistiqueMultiplication(models.Model):
    """Taux de réussite d'un enfant sur un fait de multiplication donné.

    3×7 et 7×3 sont le même fait : on range toujours le plus petit facteur dans
    facteur_min, pour que les deux sens partagent la même ligne de statistiques
    (voir enregistrer_resultat, le seul point d'entrée pour écrire ici).
    """

    enfant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="statistiques_multiplication",
        verbose_name="enfant",
    )
    facteur_min = models.PositiveSmallIntegerField("petit facteur")
    facteur_max = models.PositiveSmallIntegerField("grand facteur")
    nb_essais = models.PositiveIntegerField("nombre d'essais", default=0)
    nb_reussites = models.PositiveIntegerField("nombre de réussites", default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["enfant", "facteur_min", "facteur_max"],
                name="une_seule_ligne_par_enfant_et_par_fait",
            )
        ]
        ordering = ["facteur_min", "facteur_max"]
        verbose_name = "statistique de multiplication"
        verbose_name_plural = "statistiques de multiplication"

    def __str__(self):
        return f"{self.enfant} : {self.facteur_min}×{self.facteur_max}"

    @property
    def taux_reussite(self):
        """Pourcentage de réussite (0-100), ou None si jamais tenté."""
        if self.nb_essais == 0:
            return None
        return round(100 * self.nb_reussites / self.nb_essais)

    @classmethod
    def enregistrer_resultat(cls, enfant, a, b, reussi):
        """Point d'entrée unique pour mettre à jour les stats : gère 3×7 == 7×3."""
        facteur_min, facteur_max = min(a, b), max(a, b)
        stat, _ = cls.objects.get_or_create(
            enfant=enfant, facteur_min=facteur_min, facteur_max=facteur_max
        )
        stat.nb_essais += 1
        if reussi:
            stat.nb_reussites += 1
        stat.save()
        return stat
