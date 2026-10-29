from django.contrib import admin

from apps.core.admin import TracedAdmin

from .models import TacheEffectuee, TypeTache


@admin.register(TypeTache)
class TypeTacheAdmin(admin.ModelAdmin):
    list_display = ("nom", "points", "actif")
    list_filter = ("actif",)
    search_fields = ("nom",)


@admin.register(TacheEffectuee)
class TacheEffectueeAdmin(TracedAdmin):
    list_display = ("type_tache", "enfant", "date", "created_by")
    list_filter = ("enfant", "type_tache")
    date_hierarchy = "date"
