# Generated by Django 4.1.2 on 2022-11-17 11:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forecast", "0002_add_initial_locations"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="latitude",
            field=models.DecimalField(
                decimal_places=4,
                max_digits=7,
                validators=[
                    django.core.validators.MinValueValidator(-90),
                    django.core.validators.MaxValueValidator(90),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="location",
            name="longitude",
            field=models.DecimalField(
                decimal_places=4,
                max_digits=7,
                validators=[
                    django.core.validators.MinValueValidator(-180),
                    django.core.validators.MaxValueValidator(180),
                ],
            ),
        ),
    ]
