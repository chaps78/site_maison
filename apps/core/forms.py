import unicodedata

from django import forms
from django.core.validators import RegexValidator

from .models import User

# Le code de connexion est volontairement un simple code à 4 chiffres (pas un vrai mot de
# passe) : on ne passe donc jamais par validate_password() / AUTH_PASSWORD_VALIDATORS, qui
# le refuseraient (trop court, entièrement numérique). C'est justement pour ça que ces profils
# ont un formulaire séparé du compte qui administre Django (voir ProfilForm plus bas).
valide_code = RegexValidator(r"^\d{4}$", "Le code doit comporter exactement 4 chiffres.")


def identifiant_depuis_prenom(prenom):
    """Dérive un identifiant technique (sans accents, en minuscules) à partir du prénom.

    Cet identifiant n'est jamais affiché : il ne sert qu'en interne (clé de connexion,
    champ username de core.User) et dans l'URL de l'écran de code.
    """
    sans_accents = unicodedata.normalize("NFKD", prenom).encode("ascii", "ignore").decode()
    return sans_accents.strip().lower().replace(" ", "-")


class ConnexionForm(forms.Form):
    """Saisie du code à 4 chiffres, une fois le profil choisi par bouton."""

    code = forms.CharField(
        label="Code",
        widget=forms.PasswordInput(
            attrs={"inputmode": "numeric", "maxlength": 4, "autofocus": True}
        ),
        validators=[valide_code],
    )


class CodeForm(forms.Form):
    """Formulaire réduit : un profil non-administrateur ne peut changer que son propre code."""

    code = forms.CharField(
        label="Nouveau code à 4 chiffres",
        widget=forms.PasswordInput(attrs={"inputmode": "numeric", "maxlength": 4}),
        validators=[valide_code],
    )
    code_confirmation = forms.CharField(
        label="Confirmation du code",
        widget=forms.PasswordInput(attrs={"inputmode": "numeric", "maxlength": 4}),
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("code") and cleaned.get("code") != cleaned.get("code_confirmation"):
            self.add_error("code_confirmation", "Les deux codes ne correspondent pas.")
        return cleaned


class ProfilForm(forms.ModelForm):
    """Création/modification d'un profil par un administrateur du foyer (voir est_admin).

    Ne manipule jamais de compte is_staff/is_superuser : ceux-là restent gérés par /admin/.
    """

    code = forms.CharField(
        label="Code à 4 chiffres",
        required=False,
        widget=forms.PasswordInput(attrs={"inputmode": "numeric", "maxlength": 4}),
        validators=[valide_code],
        help_text="Laisser vide pour ne pas changer le code existant.",
    )
    code_confirmation = forms.CharField(
        label="Confirmation du code",
        required=False,
        widget=forms.PasswordInput(attrs={"inputmode": "numeric", "maxlength": 4}),
    )

    class Meta:
        model = User
        fields = ["first_name", "ordre", "est_admin", "est_parent"]
        labels = {
            "first_name": "Prénom",
            "ordre": "Ordre d'affichage",
            "est_admin": "Administrateur du foyer",
            "est_parent": "Parent (peut enregistrer les tâches des enfants)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # À la création, pas de code existant à garder : il devient obligatoire.
        if self.instance.pk is None:
            self.fields["code"].required = True
            self.fields["code_confirmation"].required = True

    def clean(self):
        cleaned = super().clean()
        code = cleaned.get("code")
        confirmation = cleaned.get("code_confirmation")
        if code and code != confirmation:
            self.add_error("code_confirmation", "Les deux codes ne correspondent pas.")
        return cleaned

    def save(self, commit=True):
        nouveau_profil = self.instance.pk is None
        profil = super().save(commit=False)
        profil.is_staff = False
        profil.is_superuser = False
        if nouveau_profil:
            base = identifiant_depuis_prenom(profil.first_name) or "membre"
            identifiant = base
            suffixe = 1
            while User.objects.filter(username=identifiant).exists():
                suffixe += 1
                identifiant = f"{base}-{suffixe}"
            profil.username = identifiant
        code = self.cleaned_data.get("code")
        if code:
            profil.set_password(code)
        if commit:
            profil.save()
        return profil
