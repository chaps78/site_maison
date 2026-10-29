from django import forms
from django.forms import inlineformset_factory

from .models import Ingredient, Recette, TypeIngredient


class TypeIngredientForm(forms.ModelForm):
    """Ajout/modification d'un type d'ingrédient du catalogue."""

    class Meta:
        model = TypeIngredient
        fields = ["nom", "quantification"]
        labels = {"nom": "Nom", "quantification": "Type de quantification"}


class TypeIngredientChoiceField(forms.ModelChoiceField):
    """Affiche l'unité à côté du nom dans la liste déroulante, ex. « Farine (kg) »."""

    def label_from_instance(self, obj):
        return f"{obj.nom} ({obj.get_quantification_display()})"


class RecetteForm(forms.ModelForm):
    """Création d'une recette : titre + commentaires (les ingrédients sont à part,
    voir IngredientFormSet, et les étapes détaillées pourront être ajoutées plus tard)."""

    class Meta:
        model = Recette
        fields = ["titre", "description"]
        labels = {"titre": "Titre", "description": "Commentaires"}
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}


class IngredientForm(forms.ModelForm):
    type_ingredient = TypeIngredientChoiceField(
        label="Ingrédient", queryset=TypeIngredient.objects.all()
    )

    class Meta:
        model = Ingredient
        fields = ["type_ingredient", "quantite"]
        labels = {"quantite": "Quantité"}


# Création : 10 lignes vides, pas de case « supprimer » (rien à supprimer encore).
# Pas de JS pour ajouter des lignes dynamiquement : les lignes laissées entièrement
# vides sont simplement ignorées à l'enregistrement.
IngredientFormSetCreation = inlineformset_factory(
    Recette, Ingredient, form=IngredientForm, extra=10, can_delete=False
)

# Modification : 3 lignes vides en plus des ingrédients existants, avec une case
# « supprimer » par ligne existante pour retirer un ingrédient de la recette.
IngredientFormSetModification = inlineformset_factory(
    Recette, Ingredient, form=IngredientForm, extra=3, can_delete=True
)
