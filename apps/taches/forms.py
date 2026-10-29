from django import forms

from apps.core.models import User

from .models import TypeTache


class TypeTacheForm(forms.ModelForm):
    """Ajout/modification d'une tâche du catalogue (réservé aux parents)."""

    class Meta:
        model = TypeTache
        fields = ["nom", "points", "actif"]
        labels = {"nom": "Nom de la tâche", "points": "Points", "actif": "Active"}


class TacheRapideForm(forms.Form):
    """Ajout rapide : qui a fait quelle tâche, toujours pour la journée en cours."""

    enfant = forms.ModelChoiceField(
        label="Enfant",
        queryset=User.objects.filter(is_staff=False, est_parent=False).order_by(
            "ordre", "first_name"
        ),
    )
    type_tache = forms.ModelChoiceField(
        label="Tâche",
        queryset=TypeTache.objects.filter(actif=True).order_by("nom"),
    )
