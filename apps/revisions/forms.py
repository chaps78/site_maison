from django import forms

TABLES_DISPONIBLES = [(n, f"Table de {n}") for n in range(1, 11)]


class ChoixTablesForm(forms.Form):
    """Choix des tables à réviser, demandé avant de démarrer le quiz."""

    tables = forms.MultipleChoiceField(
        label="Tables à réviser",
        choices=TABLES_DISPONIBLES,
        widget=forms.CheckboxSelectMultiple,
    )

    def clean_tables(self):
        # Les valeurs arrivent en chaînes depuis le formulaire HTML.
        return [int(valeur) for valeur in self.cleaned_data["tables"]]
