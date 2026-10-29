from django.contrib import admin

from .models import EtatCourses, Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("votant", "date", "premier_choix", "deuxieme_choix", "troisieme_choix")
    list_filter = ("date", "votant")
    date_hierarchy = "date"


@admin.register(EtatCourses)
class EtatCoursesAdmin(admin.ModelAdmin):
    list_display = ("recette", "date", "courses_a_faire")
    list_filter = ("date", "courses_a_faire")
    filter_horizontal = ("ingredients_manquants",)
