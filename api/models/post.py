import mimetypes
import os

from django.db import models
from django.dispatch import receiver
from django.http import HttpResponse

from api.models import User
from api.models.submission import Question
from api.models.tag import Tag


class FollowersCount(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')


class Post(models.Model):
    title = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    img_path = models.CharField(max_length=512, null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    no_of_likes = models.IntegerField(default=0)

    def get_content_image(self):
        image_path = self.img_path
        if image_path is None:
            return False
        else:
            with open(image_path, "rb") as f:
                image_file = f.read()
        img_mimetypes = mimetypes.guess_type(image_path)[0]
        return HttpResponse(image_file, content_type=img_mimetypes)


@receiver(models.signals.pre_delete, sender=Post)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    path = instance.img_path
    if path and os.path.isfile(path) and not instance.question:
        os.remove(path)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)


class LikePost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)