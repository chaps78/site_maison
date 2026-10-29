from django.shortcuts import render


def accueil(request):
    """Page d'accueil : liens vers les sections du site."""
    return render(request, "core/accueil.html")
