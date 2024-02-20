from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("storage_facility", StorageFacilityViewset)

urlpatterns = [
    path("storage/", include(router.urls)),
    path("storage/<int:pk>/", include(router.urls)),
    path(
        "storage-unit/<int:facility_id>/",
        StorageUnitView.as_view(),
        name="storage-unit",
    ),
    path(
        "storage-unit-detail/<int:storage_id>/",
        StorageUnitDetailView.as_view(),
        name="storage-unit-detail",
    ),
    path("total-storage-unit/", TotalStorageUnit.as_view(), name="total-storage-unit"),
    path(
        "available-storage-unit/",
        AvailableStorageUnit.as_view(),
        name="available-storage-unit",
    ),
    path(
        "occupied-storage-unit/",
        OccupiedStorageUnit.as_view(),
        name="occupied-storage-unit",
    ),
    path(
        "create-ratings/<int:facility_id>/",
        PostRatingsView.as_view(),
        name="create-ratings",
    ),
    path(
        "public-storage-unit/<int:facility_id>/",
        StorageUnitViewEndUser.as_view(),
        name="public-storage-unit",
    ),
    path(
        "public-storage-unit/<int:facility_id>/<int:storage_id>/",
        DetailStorageUnitViewEndUser.as_view(),
        name="public-storage-unit-detail",
    ),
    path(
        "public-storage-facility/",
        StorageFacilitySearchView.as_view(),
        name="public-storage-facility",
    ),
    path(
        "public-storage-facility/<int:pk>/",
        DetailStorageFacilityView.as_view(),
        name="public-storage-facility",
    ),
    path(
        "random-storage-facility/",
        RandomStorageFacilityView.as_view(),
        name="random-storage-facility",
    ),
    path("create-feature/", CreateFeatureView.as_view(), name="create-feature"),
    path(
        "update-destroy-feature/<int:pk>/",
        UpdateDeleteFeatureView.as_view(),
        name="update-destroy-feature",
    ),
    path("create-image/", CreateImageView.as_view(), name="create-image"),
    path("destroy-image/<int:pk>/", DeleteImageView.as_view(), name="destroy-image"),
    path("get-storage-unit/", DistinctStorageUnit.as_view(), name="get-storage-unit"),
    path(
        "get-storage-facility/",
        DistinctStorageFacility.as_view(),
        name="get-storage-facility",
    ),
]
