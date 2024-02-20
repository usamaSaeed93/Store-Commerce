from django.contrib import admin

from .models import *


# Register your models here.
class StorageFacilityOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "unit_order", "pending", "completed", "feedback"]
    list_filter = ["pending", "completed", "feedback"]


class UserOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "slug", "business_type", "total_price", "created_at"]


admin.site.register(MoverOrder)
admin.site.register(OraganizerOrder)
admin.site.register(Cart)
admin.site.register(UserOrder, UserOrderAdmin)
admin.site.register(StorageFacilityOrder, StorageFacilityOrderAdmin)
