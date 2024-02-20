from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("mover", MoverOrderViewset)
router.register("admin_mover", AdminMoverOrderViewset)
router.register("organizer", OrganizersOrderViewset)
router.register("admin_organizer", AdminOrganizersOrderViewset)

urlpatterns = [
    path("order/", include(router.urls)),
    path("order/<int:pk>/", include(router.urls)),
    path("add-to-cart/", CartView.as_view(), name="add-to-cart"),
    path("order-place/", OrderPlaceView.as_view(), name="order-place"),
    path(
        "get-order-admin/",
        GetAdminStorageUnitOrderView.as_view(),
        name="get-order-admin",
    ),
    path(
        "get-recent-order-admin/",
        GetRecentAdminStorageFacilityView.as_view(),
        name="get-recent-order-admin",
    ),
    path(
        "update-retrieve-order-admin/<int:order_id>/",
        UpdateStorageOrderAdmin.as_view(),
        name="update-retrieve-order-admin",
    ),
    path(
        "get-order-user/", GetUserStorageFacilityView.as_view(), name="get-order-user"
    ),
    path(
        "get-detail-order-user/<int:order_id>/",
        GetUserDetailStorageFacilityOrderView.as_view(),
        name="get-order-user",
    ),
    path(
        "update-order-user/<int:order_id>/",
        UpdateStorageOrderUser.as_view(),
        name="update-order-user",
    ),
]
