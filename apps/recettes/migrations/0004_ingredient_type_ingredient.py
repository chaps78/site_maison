# Remplace les champs libres nom/unite d'Ingredient par une FK vers le catalogue
# TypeIngredient (voir apps/recettes/models.py). Écrite à la main : aucune ligne
# Ingredient n'existe encore en base, pas de donnée à préserver.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recettes", "0003_alter_typeingredient_quantification"),
    ]

    operations = [
        migrations.RemoveField(model_name="ingredient", name="nom"),
        migrations.RemoveField(model_name="ingredient", name="unite"),
        migrations.AddField(
            model_name="ingredient",
            name="type_ingredient",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="utilisations",
                to="recettes.typeingredient",
                verbose_name="ingrédient",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="recette",
            name="instructions",
            field=models.TextField(blank=True),
        ),
    ]
