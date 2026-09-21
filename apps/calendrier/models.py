from django.db import models
from django.db.models import F, Q

from apps.core.models import Traced


class Evenement(Traced):
    class Categorie(models.TextChoices):
        FAMILLE = "famille", "Famille"
        MAISON = "maison", "Maison"
        RENDEZ_VOUS = "rdv", "Rendez-vous"
        ANNIVERSAIRE = "anniversaire", "Anniversaire"
        LOISIRS = "loisirs", "Loisirs"
        AUTRE = "autre", "Autre"

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Stockés en UTC, affichés en heure de Buenos Aires (USE_TZ + TIME_ZONE).
    debut = models.DateTimeField("début")
    fin = models.DateTimeField()
    # Convention « journée entière » : début à 00:00 heure locale, fin = début du jour suivant.
    journee_entiere = models.BooleanField("journée entière", default=False)
    lieu = models.CharField(max_length=200, blank=True)
    categorie = models.CharField(
        "catégorie", max_length=20, choices=Categorie.choices, default=Categorie.AUTRE
    )
    # Réservé aux événements récurrents (règle iCalendar RRULE). NON UTILISÉ en v1 : le champ
    # existe pour éviter une migration délicate plus tard.
    rrule = models.TextField(null=True, blank=True)  # noqa: DJ001 (NULL voulu : « pas de règle »)

    class Meta:
        ordering = ["debut"]
        indexes = [models.Index(fields=["debut"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(fin__gte=F("debut")),
                name="evenement_fin_apres_debut",
                violation_error_message="La fin ne peut pas précéder le début.",
            )
        ]

    def __str__(self):
        return self.titre
