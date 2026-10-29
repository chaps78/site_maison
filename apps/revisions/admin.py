from django.contrib import admin

from apps.core.admin import TracedAdmin

from .models import ResultatAccentuation, StatistiqueMultiplication


@admin.register(StatistiqueMultiplication)
class StatistiqueMultiplicationAdmin(admin.ModelAdmin):
    list_display = ("enfant", "facteur_min", "facteur_max", "nb_essais", "nb_reussites")
    list_filter = ("enfant",)


@admin.register(ResultatAccentuation)
class ResultatAccentuationAdmin(TracedAdmin):
    list_display = ("created_by", "score", "total", "created_at")
    list_filter = ("created_by",)
