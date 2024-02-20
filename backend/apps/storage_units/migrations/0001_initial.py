# Generated by Django 4.2 on 2023-09-18 09:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("service_providers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StorageFacility",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("total_size", models.IntegerField(blank=True, null=True)),
                ("free_space", models.IntegerField(blank=True, null=True)),
                ("occupied_space", models.IntegerField(blank=True, null=True)),
                ("total_storage_units", models.IntegerField(blank=True, null=True)),
                ("available_storage_units", models.IntegerField(blank=True, null=True)),
                ("occupied_storage_unit", models.IntegerField(blank=True, null=True)),
                ("address", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("is_online", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("working_hours", models.CharField(max_length=255)),
                ("access_hours", models.CharField(max_length=255)),
                ("minimum_price", models.FloatField(blank=True, null=True)),
                ("average_rating", models.FloatField(blank=True, null=True)),
                ("total_ratings", models.FloatField(blank=True, null=True)),
                ("total_persons_rating", models.IntegerField(blank=True, null=True)),
                (
                    "location",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="service_providers.location",
                    ),
                ),
                (
                    "storage_provider",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="service_providers.storageunitprovider",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StorageUnit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "storage_unit_type",
                    models.CharField(
                        choices=[
                            ("climate_control", "Climate Control"),
                            ("indoor_storage", "Indoor Storage"),
                            ("outdoor", "Outdoor/Drive Up"),
                        ],
                        default="indoor_storage",
                        max_length=255,
                    ),
                ),
                ("size", models.IntegerField()),
                (
                    "description",
                    models.TextField(blank=True, max_length=255, null=True),
                ),
                ("per_unit_price", models.FloatField(blank=True, null=True)),
                ("free_space", models.IntegerField(blank=True, null=True)),
                ("occupied_space", models.IntegerField(blank=True, null=True)),
                ("is_available", models.BooleanField(default=True)),
                ("is_occupied", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "storage_facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="storage_unit",
                        to="storage_units.storagefacility",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Ratings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("facility_ratings", models.IntegerField()),
                ("comment", models.CharField(max_length=255, null=True)),
                (
                    "storage_facility",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facility_ratings",
                        to="storage_units.storagefacility",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Images",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.URLField(max_length=250)),
                (
                    "storage_facility",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facility_images",
                        to="storage_units.storagefacility",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Feature",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "features_text",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "storage_facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="features",
                        to="storage_units.storagefacility",
                    ),
                ),
            ],
        ),
    ]