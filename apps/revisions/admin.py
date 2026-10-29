from django.contrib import admin

from .models import StatistiqueMultiplication


@admin.register(StatistiqueMultiplication)
class StatistiqueMultiplicationAdmin(admin.ModelAdmin):
    list_display = ("enfant", "facteur_min", "facteur_max", "nb_essais", "nb_reussites")
    list_filter = ("enfant",)
