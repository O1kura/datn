import os
from enum import Enum
from pathlib import Path

from django.contrib.auth.models import User

from api.models.tag import Tag
from datn import settings
from django.db import models
from django.dispatch import receiver

from datn.settings import AUTH_USER_MODEL


class Submission(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False, db_index=True)
    last_ocr_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    file_count = models.IntegerField(default=0)
    user = models.ForeignKey(AUTH_USER_MODEL, default=None, on_delete=models.CASCADE, related_name='submission_set')

    class Meta:
        db_table = 'submission'


class File(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=127)
    display_name = models.CharField(max_length=127, null=True, blank=True)
    extension = models.CharField(max_length=127, null=True, blank=True)
    path = models.CharField(max_length=512)
    size = models.IntegerField(null=True, blank=True)
    submission = models.ForeignKey('Submission', on_delete=models.DO_NOTHING, related_name='file_set')
    tags = models.ManyToManyField(Tag)

    def get_content_image(self):
        image_path = self.path
        if image_path is None:
            return False
        else:
            with open(image_path, "rb") as f:
                image_file = f.read()
        return image_file

    class Meta:
        db_table = 'file'


@receiver(models.signals.pre_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    path = instance.path
    if path and os.path.isfile(path):
        os.remove(path)


class Category(Enum):
    cau_hoi = 'cau_hoi'
    cau_tra_loi = 'cau_tra_loi'
    dap_an = 'dap_an'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class Data(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    last_ocr_value = models.TextField(null=True, blank=True)
    normalized_value = models.TextField(null=True, blank=True)
    box = models.JSONField(null=True, blank=True)
    symbol_box = models.JSONField(null=True, blank=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='data_set')


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    file = models.ForeignKey(File, on_delete=models.SET_NULL, related_name='question_set', null=True)
    path = models.CharField(max_length=512, null=True, blank=True)
    display_name = models.CharField(max_length=127, null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    def get_content_image(self):
        image_path = self.path
        if image_path is None:
            return False
        else:
            with open(image_path, "rb") as f:
                image_file = f.read()
        return image_file


@receiver(models.signals.pre_delete, sender=Question)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    path = instance.path
    if path and os.path.isfile(path):
        os.remove(path)


class QuestionData(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=27, choices=Category.choices(), default=Category.cau_tra_loi.value)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_data_set')
