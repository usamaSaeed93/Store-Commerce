from django.contrib import admin

from .models import *

# Register your models here.


class StorageFacilityAdmin(admin.ModelAdmin):
    readonly_fields = [
        "total_ratings",
        "average_rating",
        "total_persons_rating",
        "total_size",
        "free_space",
        "occupied_space",
        "total_storage_units",
        "available_storage_units",
        "occupied_storage_unit",
        "minimum_price",
    ]

    list_display = (
        "id",
        "name",
        "location",
        "total_size",
        "free_space",
        "occupied_space",
        "total_storage_units",
        "available_storage_units",
        "occupied_storage_unit",
        "is_online",
        "description",
        "address",
        "working_hours",
        "access_hours",
        "minimum_price",
        "average_rating",
        "total_persons_rating",
        "created_at",
    )


class StorageUnitAdmin(admin.ModelAdmin):
    readonly_fields = ["size", "per_unit_price"]
    list_display = (
        "id",
        "name",
        "storage_unit_type",
        "size",
        "per_unit_price",
        "free_space",
        "occupied_space",
        "storage_facility",
        "is_available",
        "is_occupied",
        "per_unit_price",
        "created_at",
    )
    list_filter = [
        "is_available",
        "is_occupied",
    ]


admin.site.register(StorageFacility, StorageFacilityAdmin)
admin.site.register(StorageUnit, StorageUnitAdmin)
admin.site.register(Images)
admin.site.register(Ratings)
