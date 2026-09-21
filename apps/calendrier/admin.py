from django.contrib import admin

from apps.core.admin import TracedAdmin

from .models import Evenement


@admin.register(Evenement)
class EvenementAdmin(TracedAdmin):
    list_display = ("titre", "debut", "fin", "categorie", "journee_entiere", "created_by")
    list_filter = ("categorie", "journee_entiere")
    search_fields = ("titre", "description", "lieu")
    date_hierarchy = "debut"
    # rrule est réservé (non utilisé en v1) : on le cache pour ne pas tromper l'utilisateur.
    exclude = ("rrule",)
