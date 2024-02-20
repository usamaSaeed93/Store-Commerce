import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from .models import *


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.user_id = force_str(urlsafe_base64_decode(self.user_id))

        self.notification_group_name = f"user_{self.user_id}"

        await self.channel_layer.group_add(
            self.notification_group_name, self.channel_name
        )

        await self.accept()
        notification = await database_sync_to_async(self.get_notifications)()

        await self.send(json.dumps(notification))

    async def disconnect(self, event):
        await self.channel_layer.group_discard(
            self.notification_group_name, self.channel_name
        )
        await self.close()

    async def notify(self, event):
        notification = event["notification"]
        await self.send(text_data=json.dumps(notification))

    def get_notifications(self):
        data_noti = []
        notifications = Notifications.objects.filter(user__id=self.user_id)
        total_count = Notifications.objects.filter(
            user__id=self.user_id, is_read=False
        ).count()
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
        return data_noti
