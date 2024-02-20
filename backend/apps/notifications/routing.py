from django.urls import path

from .consumer import NotificationConsumer

websocket_urlpatterns = [
    path("app/ws/notifications/<str:user_id>/", NotificationConsumer.as_asgi()),
]
