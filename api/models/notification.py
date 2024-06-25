from enum import Enum

from django.db import models

from api.models import User


class NotificationType(Enum):
    get_followed = 'get_followed'
    new_post = 'new_post'
    new_comment = 'new_comment'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class Notification(models.Model):
    id = models.BigAutoField(primary_key=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_by_actor')
    type = models.CharField(max_length=27, choices=NotificationType.choices(), db_index=True)
    message = models.TextField(null=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)  # Assuming you have a Post model
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    is_read = models.BooleanField(default=False, db_index=True)
