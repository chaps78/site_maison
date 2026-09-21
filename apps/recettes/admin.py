from django.contrib import admin

from apps.core.admin import TracedAdmin

from .models import Ingredient, Recette, Tag


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 3


@admin.register(Recette)
class RecetteAdmin(TracedAdmin):
    list_display = ("titre", "favori", "created_by", "created_at")
    list_filter = ("favori", "tags")
    search_fields = ("titre", "description")
    filter_horizontal = ("tags",)
    inlines = [IngredientInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug")
    search_fields = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}
