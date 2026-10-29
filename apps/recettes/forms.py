from django import forms

from .models import TypeIngredient


class TypeIngredientForm(forms.ModelForm):
    """Ajout/modification d'un type d'ingrédient du catalogue."""

    class Meta:
        model = TypeIngredient
        fields = ["nom", "quantification"]
        labels = {"nom": "Nom", "quantification": "Type de quantification"}
