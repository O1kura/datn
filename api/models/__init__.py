# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    email = models.CharField(max_length=127, unique=True)
    first_name = models.CharField(null=True, blank=True, max_length=100)
    last_name = models.CharField(null=True, blank=True, max_length=100)
    name = models.CharField(null=True, blank=True, max_length=100)
    phone = models.CharField(max_length=20, null=True)
    profile_path = models.CharField(null=True, max_length=512)
    thumb_profile_path = models.CharField(null=True, max_length=512)

    class Meta:
        db_table = 'auth_user'
        indexes = [
            models.Index(fields=['email', 'name'])
        ]

