import pytest

from apps.taches.paliers import progression


@pytest.mark.parametrize(
    ("total", "palier_suivant", "paliers_atteints", "pourcentage"),
    [
        (0, 300, 0, 0),
        (150, 300, 0, 50),
        (300, 400, 1, 0),
        (350, 400, 1, 50),
        (400, 500, 2, 0),
        (450, 500, 2, 50),
        (500, None, 3, 100),
        (999, None, 3, 100),
    ],
)
def test_progression_vers_le_palier_suivant(total, palier_suivant, paliers_atteints, pourcentage):
    resultat = progression(total)
    assert resultat["palier_suivant"] == palier_suivant
    assert resultat["paliers_atteints"] == paliers_atteints
    assert resultat["pourcentage"] == pourcentage


def test_un_total_negatif_ne_fait_pas_planter_la_barre():
    """Une punition peut rendre le total négatif : la barre reste à 0%, pas en dessous."""
    resultat = progression(-20)
    assert resultat["pourcentage"] == 0
    assert resultat["palier_suivant"] == 300
