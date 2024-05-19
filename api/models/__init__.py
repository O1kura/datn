# users/models.py
import mimetypes

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.http import HttpResponse

from api.utils.utils import get_path


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

    def get_photo(self):
        real_path = get_path(self.profile_path)
        img_mimetypes = mimetypes.guess_type(real_path)[0]
        with open(real_path, "rb") as f:
            image_file = f.read()
        return HttpResponse(image_file, content_type=img_mimetypes)

    def get_thumb_photo(self):
        real_path = get_path(self.thumb_profile_path)
        img_mimetypes = mimetypes.guess_type(real_path)[0]
        with open(real_path, "rb") as f:
            image_file = f.read()
        return HttpResponse(image_file, content_type=img_mimetypes)
