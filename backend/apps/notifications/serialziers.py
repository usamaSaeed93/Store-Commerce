from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import serializers

from apps.service_providers.serializers import UserSerializer

from .models import *


class NotificationSerializer(serializers.ModelSerializer):
    """
    This is the serialzier which serializes the
    notification data.
    """

    user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Notifications
        fields = ["user", "title", "body", "url", "is_read"]

    def create(self, validated_data):
        user = self.context["request"].user
        notification = Notifications.objects.create(user=user, **validated_data)
        channel_layer = get_channel_layer()
        data_noti = []
        notifications = Notifications.objects.filter(user=user)
        total_count = Notifications.objects.filter(user=user, is_read=False).count()
        for data in notifications:
            data_noti.append(
                {
                    "id": data.pk,
                    "title": data.title,
                    "body": data.body,
                    "url": data.url,
                    "is_read": data.is_read,
                    "unread_notifications": total_count,
                }
            )
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}", {"type": "notify", "notification": data_noti}
        )

        return notification

    def update(self, instance, validated_data):
        instance.is_read = validated_data.get("is_read", instance.is_read)
        user = validated_data.get("user", instance.user)
        instance.save()
        channel_layer = get_channel_layer()
        data_noti = []
        notifications = Notifications.objects.filter(user=user)
        total_count = Notifications.objects.filter(user=user, is_read=False).count()
        for data in notifications:
            data_noti.append(
                {
                    "id": data.pk,
                    "title": data.title,
                    "body": data.body,
                    "url": data.url,
                    "is_read": data.is_read,
                    "unread_notifications": total_count,
                }
            )
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}", {"type": "notify", "notification": data_noti}
        )

        return instance
