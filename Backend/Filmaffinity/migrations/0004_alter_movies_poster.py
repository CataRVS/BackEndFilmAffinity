# Generated by Django 4.2.11 on 2024-05-16 13:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Filmaffinity", "0003_alter_platformusers_first_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movies",
            name="poster",
            field=models.ImageField(
                blank=True,
                default="posters/default.png",
                null=True,
                upload_to="posters/",
            ),
        ),
    ]