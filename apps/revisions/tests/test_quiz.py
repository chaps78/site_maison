from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.revisions.models import StatistiqueMultiplication


@pytest.fixture
def questions_fixes():
    """10 questions déterministes : table de 7, b de 1 à 10."""
    return [(7, b) for b in range(1, 11)]


def _demarrer_quiz(client, questions_fixes):
    with (
        patch("apps.revisions.views.random.choice", side_effect=[q[0] for q in questions_fixes]),
        patch("apps.revisions.views.random.randint", side_effect=[q[1] for q in questions_fixes]),
    ):
        return client.post(reverse("revisions:multiplication_config"), {"tables": ["7"]})


@pytest.mark.django_db
def test_il_faut_choisir_au_moins_une_table(client, philippe):
    client.force_login(philippe)
    reponse = client.post(reverse("revisions:multiplication_config"), {"tables": []})
    assert reponse.status_code == 200  # formulaire réaffiché avec l'erreur
    assert client.session.get("quiz_multiplication") is None


@pytest.mark.django_db
def test_parcours_complet_du_quiz(client, philippe, questions_fixes):
    client.force_login(philippe)
    reponse = _demarrer_quiz(client, questions_fixes)
    assert reponse.status_code == 302
    assert reponse.url == reverse("revisions:multiplication_jouer")

    # 5 bonnes réponses, 5 mauvaises.
    for i, (a, b) in enumerate(questions_fixes):
        bonne_reponse = a * b
        valeur_envoyee = bonne_reponse if i < 5 else bonne_reponse + 1
        reponse = client.post(
            reverse("revisions:multiplication_jouer"), {"reponse": valeur_envoyee}
        )

    assert reponse.status_code == 302
    assert reponse.url == reverse("revisions:multiplication_resultat")

    reponse = client.get(reverse("revisions:multiplication_resultat"))
    contenu = reponse.content.decode()
    assert "5 / 10" in contenu
    assert "seconde" in contenu

    # Chaque (7, b) est un fait distinct ici (b va de 1 à 10) : 10 lignes de stats.
    assert StatistiqueMultiplication.objects.filter(enfant=philippe).count() == 10
    stat_7x1 = StatistiqueMultiplication.objects.get(enfant=philippe, facteur_min=1, facteur_max=7)
    assert stat_7x1.nb_essais == 1
    assert stat_7x1.nb_reussites == 1  # c'était la 1ère question, dans les 5 bonnes


@pytest.mark.django_db
def test_sans_quiz_en_session_la_page_de_jeu_redirige_vers_la_config(client, philippe):
    client.force_login(philippe)
    reponse = client.get(reverse("revisions:multiplication_jouer"))
    assert reponse.status_code == 302
    assert reponse.url == reverse("revisions:multiplication_config")


@pytest.mark.django_db
def test_la_matrice_de_statistiques_s_affiche(client, philippe, josephine):
    StatistiqueMultiplication.enregistrer_resultat(josephine, 6, 8, reussi=True)
    client.force_login(philippe)
    reponse = client.get(reverse("revisions:multiplication_statistiques"))
    assert reponse.status_code == 200
    assert "Joséphine" in reponse.content.decode()
