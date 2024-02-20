from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

from apps.Auth.models import User


class Location(models.Model):
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=3, blank=True, null=True)
    county = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.IntegerField(blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    point = models.PointField(null=True, blank=True)

    def __str__(self):
        return f"{self.address}"


class ServiceProvider(models.Model):
    name = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    fax_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=254)
    website = models.CharField(max_length=250, blank=True, null=True)
    facebook = models.CharField(max_length=250, blank=True, null=True)
    instagram = models.CharField(max_length=250, blank=True, null=True)
    twitter = models.CharField(max_length=250, blank=True, null=True)
    google_buisness = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name}"


class StorageUnitProvider(ServiceProvider):
    location = models.ManyToManyField(
        Location,
        through="storage_units.StorageFacility",
        related_name="storage_location",
        blank=True,
    )


class Movers(ServiceProvider):
    working_hours = models.CharField(max_length=200)
    location = models.ManyToManyField(
        Location, related_name="movers_location", blank=True
    )


class Organizers(ServiceProvider):
    unit_numbers = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(111111)]
    )
    size = models.IntegerField()
    location = models.ManyToManyField(
        Location, related_name="organizers_location", blank=True
    )
