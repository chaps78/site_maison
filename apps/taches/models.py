from django.conf import settings
from django.db import models

from apps.core.models import Traced


class TypeTache(models.Model):
    """Une tâche du catalogue (« mettre la table », « lecture »...) et ses points."""

    nom = models.CharField(max_length=100, unique=True)
    points = models.PositiveSmallIntegerField(default=1)
    # Pour retirer une tâche du catalogue sans casser l'historique des tâches déjà faites
    # (TacheEffectuee.type_tache est en PROTECT : impossible de la supprimer pour de vrai).
    actif = models.BooleanField("active", default=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "type de tâche"
        verbose_name_plural = "types de tâche"

    def __str__(self):
        return self.nom


class TacheEffectuee(Traced):
    """Une tâche effectuée par un enfant, un jour donné (le foyer peut en faire plusieurs/jour)."""

    enfant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="taches_effectuees",
        verbose_name="enfant",
    )
    type_tache = models.ForeignKey(
        TypeTache, on_delete=models.PROTECT, related_name="executions", verbose_name="tâche"
    )
    # Jour local (Buenos Aires) où la tâche a été faite, renseigné par la vue avec
    # timezone.localdate() — jamais date.today() (voir apps/calendrier/tests/test_fuseau.py).
    date = models.DateField("date")

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [models.Index(fields=["enfant", "date"])]
        verbose_name = "tâche effectuée"
        verbose_name_plural = "tâches effectuées"

    def __str__(self):
        return f"{self.type_tache} – {self.enfant} ({self.date})"
