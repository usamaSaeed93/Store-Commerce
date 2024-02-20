from django.urls import path

from .views import *

urlpatterns = [
    path("post-notification/", NotificationViews.as_view(), name="post-notification"),
    path(
        "update-notification/<int:id>/",
        UpdateNotificationViews.as_view(),
        name="update-notification",
    ),
]
