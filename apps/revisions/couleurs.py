"""Couleur d'une cellule de la matrice de statistiques, calculée en Python (pas de JS)."""

# Rouge doux (0%) -> vert doux (100%), interpolation linéaire.
_ROUGE = (0xF4, 0x43, 0x36)
_VERT = (0x2E, 0x7D, 0x32)
_NEUTRE = "#e2e5e9"  # jamais tenté


def couleur_pour_taux(taux):
    if taux is None:
        return _NEUTRE
    t = max(0, min(100, taux)) / 100
    r, g, b = (
        round(depart + (fin - depart) * t) for depart, fin in zip(_ROUGE, _VERT, strict=True)
    )
    return f"#{r:02x}{g:02x}{b:02x}"
