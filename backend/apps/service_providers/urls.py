from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.service_providers import views

router = DefaultRouter()
router.register("movers", views.MoversViewset)
router.register("organizers", views.OrganizersViewset)
router.register("storage_unit_provider", views.StorageUnitProviderViewset)


urlpatterns = [
    path("service/", include(router.urls)),
    path("service/<int:pk>/", include(router.urls)),
    path("location/", views.LocationView.as_view(), name="location"),
    path("public-movers/", views.MoversView.as_view(), name="public-movers"),
    path(
        "public-organizers/", views.OrganizersView.as_view(), name="public-organizers"
    ),
    path(
        "public-movers/<int:pk>/",
        views.DetailMoversView.as_view(),
        name="public-movers",
    ),
    path(
        "public-organizers/<int:pk>/",
        views.DetailOrganizersView.as_view(),
        name="public-organizers",
    ),
]
