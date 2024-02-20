import math as m

from django.db import models

from apps.Auth.models import User
from apps.service_providers.models import Location, StorageUnitProvider


# Create your models here.
class StorageFacility(models.Model):
    name = models.CharField(max_length=255)
    storage_provider = models.ForeignKey(
        StorageUnitProvider, on_delete=models.CASCADE, null=True, blank=True
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, null=True, blank=True
    )
    total_size = models.IntegerField(blank=True, null=True)
    free_space = models.IntegerField(blank=True, null=True)
    occupied_space = models.IntegerField(blank=True, null=True)
    total_storage_units = models.IntegerField(blank=True, null=True)
    available_storage_units = models.IntegerField(blank=True, null=True)
    occupied_storage_unit = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_online = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    working_hours = models.CharField(max_length=255)
    access_hours = models.CharField(max_length=255)
    minimum_price = models.FloatField(blank=True, null=True)
    average_rating = models.FloatField(blank=True, null=True)
    total_ratings = models.FloatField(blank=True, null=True)
    total_persons_rating = models.IntegerField(blank=True, null=True)

    @property
    def total_size_field(self):
        if self.total_size:
            if self.total_size >= 0:
                result = f"{round(m.sqrt(self.total_size))} x {round(m.sqrt(self.total_size))}"
                return result
            else:
                return "0 x 0"
        else:
            return "0 x 0"

    @property
    def free_space_field(self):
        if self.free_space:
            if self.free_space >= 0:
                result = f"{round(m.sqrt(self.free_space))} x {round(m.sqrt(self.free_space))}"
                return result
            else:
                return "0 x 0"
        else:
            return "0 x 0"

    @property
    def occupied_space_field(self):
        if self.occupied_space:
            if self.free_space >= 0:
                result = f"{round(m.sqrt(self.occupied_space))} x {round(m.sqrt(self.occupied_space))}"
                return result
            else:
                return "0 x 0"
        else:
            return "0 x 0"

    def __str__(self):
        return self.name


class Images(models.Model):
    storage_facility = models.ForeignKey(
        StorageFacility,
        on_delete=models.CASCADE,
        null=True,
        related_name="facility_images",
    )
    image = models.URLField(max_length=250)


class Feature(models.Model):
    storage_facility = models.ForeignKey(
        StorageFacility, on_delete=models.CASCADE, related_name="features"
    )
    features_text = models.CharField(max_length=255, blank=True, null=True)


class Ratings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    storage_facility = models.ForeignKey(
        StorageFacility,
        on_delete=models.CASCADE,
        null=True,
        related_name="facility_ratings",
    )
    facility_ratings = models.IntegerField()
    comment = models.CharField(max_length=255, null=True)


STORAGE_TYPES = (
    ("climate_control", "Climate Control"),
    ("indoor_storage", "Indoor Storage"),
    ("outdoor", "Outdoor/Drive Up"),
)


class StorageUnit(models.Model):
    name = models.CharField(max_length=255)
    storage_unit_type = models.CharField(
        max_length=255, choices=STORAGE_TYPES, default="indoor_storage"
    )
    storage_facility = models.ForeignKey(
        StorageFacility, on_delete=models.CASCADE, related_name="storage_unit"
    )
    size = models.IntegerField()
    description = models.TextField(max_length=255, blank=True, null=True)
    per_unit_price = models.FloatField(blank=True, null=True)
    free_space = models.IntegerField(blank=True, null=True)
    occupied_space = models.IntegerField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_occupied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def size_field(self):
        if self.size:
            result = f"{round(m.sqrt(self.size))} x {round(m.sqrt(self.size))}"
            return result
        else:
            return "0 x 0"

    @property
    def free_space_field(self):
        if self.free_space:
            if self.free_space >= 0:
                result = f"{round(m.sqrt(self.free_space))} x {round(m.sqrt(self.free_space))}"
                return result
            else:
                return "0 x 0"
        else:
            return "0 x 0"

    @property
    def occupied_space_field(self):
        if self.occupied_space:
            if self.occupied_space >= 0:
                result = f"{round(m.sqrt(self.occupied_space))} x {round(m.sqrt(self.occupied_space))}"
                return result
            else:
                return "0 x 0"
        else:
            return "0 x 0"
