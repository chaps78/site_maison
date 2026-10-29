from django.core.management.base import BaseCommand

from apps.core.models import User

# (identifiant technique, prénom affiché, ordre d'affichage)
PROFILS_INITIAUX = [
    ("papa", "Papa", 1),
    ("maman", "Maman", 2),
    ("philippe", "Philippe", 3),
    ("josephine", "Joséphine", 4),
]

CODE_PAR_DEFAUT = "0000"


class Command(BaseCommand):
    help = (
        "Crée les 4 profils du foyer (Papa, Maman, Philippe, Joséphine) s'ils n'existent pas "
        "encore, avec le code temporaire 0000 (à changer ensuite via /profils/)."
    )

    def handle(self, *args, **options):
        for username, prenom, ordre in PROFILS_INITIAUX:
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"{prenom} existe déjà, ignoré.")
                continue
            # set_password() ne passe pas par AUTH_PASSWORD_VALIDATORS : c'est volontaire,
            # ces codes sont des codes à 4 chiffres, pas de vrais mots de passe (voir forms.py).
            profil = User(username=username, first_name=prenom, ordre=ordre, is_staff=False)
            profil.set_password(CODE_PAR_DEFAUT)
            profil.save()
            self.stdout.write(
                self.style.SUCCESS(f"{prenom} créé avec le code temporaire {CODE_PAR_DEFAUT}.")
            )
