"""Paliers de points du mois, affichés en barre de progression sur la page Tâches.

Seuils fixes pour l'instant (pas de catalogue dédié) : changer PALIERS au besoin.
"""

PALIERS = [300, 400, 500]


def progression(total):
    """Où en est un enfant par rapport aux paliers, pour la barre de progression.

    Renvoie palier_suivant (le prochain seuil, ou None si tous dépassés),
    pourcentage (0-100, vers ce palier) et paliers_atteints (combien sont dépassés).
    """
    # Une punition fait baisser le total mais pas « reculer » la barre sous 0.
    total = max(total, 0)
    paliers_atteints = sum(1 for palier in PALIERS if total >= palier)

    if paliers_atteints == len(PALIERS):
        return {"palier_suivant": None, "pourcentage": 100, "paliers_atteints": paliers_atteints}

    palier_suivant = PALIERS[paliers_atteints]
    palier_precedent = PALIERS[paliers_atteints - 1] if paliers_atteints > 0 else 0
    taille_palier = palier_suivant - palier_precedent
    pourcentage = round(100 * (total - palier_precedent) / taille_palier)
    return {
        "palier_suivant": palier_suivant,
        "pourcentage": pourcentage,
        "paliers_atteints": paliers_atteints,
    }
