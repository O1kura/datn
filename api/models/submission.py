from django.db import models


class Submission(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False, db_index=True)
    last_ocr_time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
