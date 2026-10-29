from django.shortcuts import render


def liste_recettes(request):
    """Liste des recettes (à construire)."""
    return render(request, "recettes/liste_recettes.html")
