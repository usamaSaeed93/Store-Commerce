import random

from django.db import models
from django.utils.text import slugify

from apps.Auth.models import User
from apps.service_providers.models import Location, Movers, Organizers
from apps.storage_units.models import StorageUnit

# Create your models here.
BUSINESS_TYPE = [
    ("commercial", "Commercial"),
    ("public", "Public"),
    ("business", "Business"),
    ("personal", "Personal"),
]


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    from_location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    business_type = models.CharField(
        max_length=255, choices=BUSINESS_TYPE, default="personal"
    )
    pending = models.BooleanField(default=False)
    proccess = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    storage_unit = models.ManyToManyField(StorageUnit, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)
    business_type = models.CharField(
        max_length=255, choices=BUSINESS_TYPE, default="personal"
    )
    total_price = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        gen_ran_num = random.randrange(100010, 999999)
        randomLowerLetter = chr(random.randint(ord("a"), ord("z")))
        randomUpperLetter = chr(random.randint(ord("A"), ord("Z")))
        if not self.slug:
            self.slug = slugify(
                randomUpperLetter
                + randomLowerLetter
                + str(self.id)
                + randomUpperLetter
                + str(gen_ran_num)
                + randomLowerLetter
                + str(self.id)
                + randomUpperLetter
            )
            self.save()


class StorageFacilityOrder(models.Model):
    order = models.ForeignKey(
        UserOrder, on_delete=models.CASCADE, null=True, related_name="order"
    )
    unit_order = models.ForeignKey(
        StorageUnit, on_delete=models.CASCADE, null=True, related_name="unit_order"
    )
    feedback = models.BooleanField(default=False)
    pending = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    months = models.IntegerField(default=1)
    starting_date = models.DateField()
    ending_date = models.DateField(blank=True, null=True)


class MoverOrder(Order):
    mover_order = models.ForeignKey(Movers, on_delete=models.CASCADE, null=True)
    size = models.IntegerField()


class OraganizerOrder(Order):
    organizer_order = models.ForeignKey(Organizers, on_delete=models.CASCADE, null=True)
    to_location = models.ForeignKey(
        Location, on_delete=models.CASCADE, null=True, related_name="to_location"
    )
    size = models.IntegerField()
    time = models.CharField(max_length=200)
