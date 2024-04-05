import os
from enum import Enum
from pathlib import Path

from django.contrib.auth.models import User

from datn import settings
from django.db import models
from django.dispatch import receiver


class Submission(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False, db_index=True)
    last_ocr_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    user = models.ForeignKey(User , default=None, on_delete=models.CASCADE, related_name='submission_set')

    class Meta:
        db_table = 'submission'


class File(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=127)
    extension = models.CharField(max_length=127, null=True, blank=True)
    path = models.CharField(max_length=512)
    size = models.IntegerField(null=True, blank=True)
    submission = models.ForeignKey('Submission', on_delete=models.DO_NOTHING, related_name='file_set')

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except ValueError:
            url = ''
        return url

    class Meta:
        db_table = 'file'
@receiver(models.signals.pre_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    img = instance.image
    old_file = instance.imageURL
    path = Path(os.path.join(settings.MEDIA_ROOT, img.name))

    if old_file != '':
        if os.path.isfile(path):
            os.remove(path)


@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.id:
        return False

    product = File.objects.get(id=instance.id)
    img = product.image
    old_file = product.imageURL
    path = Path(os.path.join(settings.MEDIA_ROOT, img.name))

    if old_file == '':
        return False

    new_file = instance.imageURL
    if not old_file == new_file:
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
    value = models.TextField(null=True, blank=True)
    normalized_value = models.TextField(null=True, blank=True)
    box = models.JSONField(null=True, blank=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='data_set')


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    category = models.CharField(max_length=27, choices=Category.choices(), default=Category.cau_tra_loi.value)
    box = models.JSONField(null=True, blank=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='question_set')
    image = models.ImageField(upload_to='question')


class QuestionData(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=27, choices=Category.choices(), default=Category.cau_tra_loi.value)
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_data_set')
