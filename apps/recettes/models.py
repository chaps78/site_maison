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


class TypeIngredient(models.Model):
    """Catalogue des ingrédients (« Farine », « Lait »...), choisi dans les lignes
    d'ingrédients d'une recette (voir Ingredient) ; sera aussi la base de l'app courses.
    """

    class Quantification(models.TextChoices):
        GRAMME = "g", "Grammes (g)"
        KILOGRAMME = "kg", "Kilogrammes (kg)"
        LITRE = "l", "Litres (l)"
        CENTILITRE = "cl", "Centilitres (cl)"
        QUANTITE = "quantite", "Quantité (pièce)"

    nom = models.CharField(max_length=200, unique=True)
    quantification = models.CharField(
        "type de quantification", max_length=10, choices=Quantification.choices
    )

    class Meta:
        ordering = ["nom"]
        verbose_name = "type d'ingrédient"
        verbose_name_plural = "types d'ingrédient"

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
    # Optionnel : la création rapide ne demande qu'un titre, des ingrédients et un
    # commentaire (description) ; les étapes détaillées peuvent être ajoutées plus tard.
    instructions = models.TextField(blank=True)
    photo = models.ImageField(upload_to="recettes/%Y/%m/", blank=True)
    favori = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True, related_name="recettes")

    class Meta:
        ordering = ["titre"]

    def __str__(self):
        return self.titre


class Ingredient(models.Model):
    """Une ligne d'ingrédient d'une recette : un type d'ingrédient du catalogue + une
    quantité. L'unité n'est plus saisie ici : elle vient de type_ingredient.quantification.
    """

    recette = models.ForeignKey(Recette, on_delete=models.CASCADE, related_name="ingredients")
    # PROTECT : on ne peut pas supprimer un type d'ingrédient utilisé par une recette
    # (voir type_ingredient_supprimer, qui affiche un message plutôt qu'une erreur 500).
    type_ingredient = models.ForeignKey(
        TypeIngredient,
        on_delete=models.PROTECT,
        related_name="utilisations",
        verbose_name="ingrédient",
    )
    quantite = models.DecimalField(
        "quantité", max_digits=8, decimal_places=2, null=True, blank=True
    )
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "id"]

    def __str__(self):
        return str(self.type_ingredient)
