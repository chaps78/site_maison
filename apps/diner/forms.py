from django import forms

from apps.recettes.models import Recette

from .models import Vote


class VoteForm(forms.ModelForm):
    """Vote du jour : 1 à 3 plats classés (seul le 1er choix est obligatoire)."""

    class Meta:
        model = Vote
        fields = ["premier_choix", "deuxieme_choix", "troisieme_choix"]
        labels = {
            "premier_choix": "1er choix (3 points)",
            "deuxieme_choix": "2e choix (2 points)",
            "troisieme_choix": "3e choix (1 point)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # blank=True côté modèle (pour SET_NULL si une recette est supprimée) ne doit
        # pas rendre le 1er choix facultatif dans le formulaire.
        self.fields["premier_choix"].required = True
        for nom in self.fields:
            self.fields[nom].queryset = Recette.objects.order_by("titre")

    def clean(self):
        cleaned = super().clean()
        choix = [
            cleaned.get("premier_choix"),
            cleaned.get("deuxieme_choix"),
            cleaned.get("troisieme_choix"),
        ]
        remplis = [c for c in choix if c is not None]
        if len(remplis) != len(set(remplis)):
            self.add_error(None, "Choisis 3 plats différents.")
        return cleaned
