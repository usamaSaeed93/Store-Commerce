from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import Location, Movers, Organizers, StorageUnitProvider


class LocationAdmin(LeafletGeoAdmin):
    list_display = (
        "address",
        "city",
        "country",
        "country_code",
        "county",
        "postcode",
        "district",
        "lat",
        "lon",
        "point",
    )


class StorageUnitProviderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "phone_number",
        "fax_number",
        "email",
    )


admin.site.register(Location, LocationAdmin)
admin.site.register(StorageUnitProvider, StorageUnitProviderAdmin)
admin.site.register(Movers)
admin.site.register(Organizers)
