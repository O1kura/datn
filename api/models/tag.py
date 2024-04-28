from django.db import models


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    tag_name = models.CharField(max_length=127, unique=True)

    def __str__(self):
        return "#" + str(self.tag_name)

    class Meta:
        indexes = [
            models.Index(fields=['tag_name'])
        ]
