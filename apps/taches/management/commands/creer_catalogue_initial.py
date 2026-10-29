from django.core.management.base import BaseCommand

from apps.taches.models import TypeTache

# (nom, points) — valeurs de départ à ajuster ensuite via /taches/catalogue/.
CATALOGUE_INITIAL = [
    ("Mettre la table", 1),
    ("Débarrasser", 1),
    ("Se brosser les dents tout seul", 1),
    ("Lecture", 2),
]


class Command(BaseCommand):
    help = (
        "Crée le catalogue de tâches de départ (mettre la table, débarrasser, se brosser "
        "les dents, lecture) s'il n'existe pas déjà. Les points sont des valeurs de départ, "
        "à ajuster ensuite via /taches/catalogue/."
    )

    def handle(self, *args, **options):
        for nom, points in CATALOGUE_INITIAL:
            if TypeTache.objects.filter(nom=nom).exists():
                self.stdout.write(f"« {nom} » existe déjà, ignoré.")
                continue
            TypeTache.objects.create(nom=nom, points=points)
            self.stdout.write(self.style.SUCCESS(f"« {nom} » créé ({points} pt)."))
