import pytest
from django.db.models import ProtectedError

from apps.taches.models import TacheEffectuee, TypeTache


@pytest.mark.django_db
def test_str_type_tache():
    assert str(TypeTache.objects.create(nom="Lecture", points=2)) == "Lecture"


@pytest.mark.django_db
def test_on_ne_peut_pas_supprimer_une_tache_du_catalogue_deja_utilisee(maman, josephine):
    tache_type = TypeTache.objects.create(nom="Lecture", points=2)
    TacheEffectuee.objects.create(
        enfant=josephine, type_tache=tache_type, date="2026-10-29", created_by=maman
    )
    with pytest.raises(ProtectedError):
        tache_type.delete()
