from django.db import models

from apps.Auth.models import User


# Create your models here.
class Notifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="receiver"
    )
    title = models.CharField(max_length=255)
    body = models.CharField(max_length=250)
    url = models.URLField(max_length=255, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
