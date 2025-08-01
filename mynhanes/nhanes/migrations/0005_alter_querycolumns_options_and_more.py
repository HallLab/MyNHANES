# Generated by Django 5.0.8 on 2024-08-27 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("nhanes", "0004_alter_rulevariable_dataset"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="querycolumns",
            options={"verbose_name_plural": "Query: Columns"},
        ),
        migrations.AlterField(
            model_name="queryfilter",
            name="filter_name",
            field=models.CharField(
                choices=[
                    ("variable__variable", "Variable Code"),
                    ("variable__description", "Variable Name"),
                    ("cycle__cycle", "Cycle"),
                    ("dataset__group__group", "Group"),
                    ("dataset__dataset", "Dataset Code"),
                    ("dataset__description", "Dataset Name"),
                    ("version__version", "Version"),
                ],
                default="variable",
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="variablecycle",
            name="target",
            field=models.TextField(),
        ),
    ]
