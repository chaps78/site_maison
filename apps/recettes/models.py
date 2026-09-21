from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import Traced


class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Recette(Traced):
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    temps_preparation = models.PositiveSmallIntegerField(
        "temps de préparation", null=True, blank=True, help_text="En minutes."
    )
    temps_cuisson = models.PositiveSmallIntegerField(
        "temps de cuisson", null=True, blank=True, help_text="En minutes."
    )
    portions = models.PositiveSmallIntegerField(default=4, validators=[MinValueValidator(1)])
    instructions = models.TextField()
    photo = models.ImageField(upload_to="recettes/%Y/%m/", blank=True)
    favori = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True, related_name="recettes")

    class Meta:
        ordering = ["titre"]

    def __str__(self):
        return self.titre


class Ingredient(models.Model):
    class Unite(models.TextChoices):
        GRAMME = "g", "g"
        KILOGRAMME = "kg", "kg"
        MILLILITRE = "ml", "ml"
        CENTILITRE = "cl", "cl"
        LITRE = "l", "l"
        CUILLERE_CAFE = "cac", "c. à café"
        CUILLERE_SOUPE = "cas", "c. à soupe"
        TASSE = "tasse", "tasse"
        PINCEE = "pincee", "pincée"
        PIECE = "piece", "pièce"
        GOUSSE = "gousse", "gousse"
        TRANCHE = "tranche", "tranche"

    recette = models.ForeignKey(Recette, on_delete=models.CASCADE, related_name="ingredients")
    nom = models.CharField(max_length=200)
    quantite = models.DecimalField(
        "quantité", max_digits=8, decimal_places=2, null=True, blank=True
    )
    # Vide = sans unité (« 2 œufs », « sel »).
    unite = models.CharField("unité", max_length=10, choices=Unite.choices, blank=True)
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "id"]

    def __str__(self):
        return self.nom
