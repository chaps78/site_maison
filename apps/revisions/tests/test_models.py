import pytest

from apps.revisions.models import StatistiqueMultiplication


@pytest.mark.django_db
def test_3x7_et_7x3_partagent_la_meme_statistique(philippe):
    StatistiqueMultiplication.enregistrer_resultat(philippe, 3, 7, reussi=True)
    StatistiqueMultiplication.enregistrer_resultat(philippe, 7, 3, reussi=False)

    stat = StatistiqueMultiplication.objects.get(enfant=philippe, facteur_min=3, facteur_max=7)
    assert stat.nb_essais == 2
    assert stat.nb_reussites == 1
    assert stat.taux_reussite == 50
    assert StatistiqueMultiplication.objects.filter(enfant=philippe).count() == 1


@pytest.mark.django_db
def test_taux_reussite_none_si_jamais_tente():
    stat = StatistiqueMultiplication(facteur_min=2, facteur_max=4)
    assert stat.taux_reussite is None


@pytest.mark.django_db
def test_deux_enfants_ont_des_statistiques_separees(philippe, josephine):
    StatistiqueMultiplication.enregistrer_resultat(philippe, 4, 4, reussi=True)
    StatistiqueMultiplication.enregistrer_resultat(josephine, 4, 4, reussi=False)

    assert StatistiqueMultiplication.objects.get(enfant=philippe).nb_reussites == 1
    assert StatistiqueMultiplication.objects.get(enfant=josephine).nb_reussites == 0
