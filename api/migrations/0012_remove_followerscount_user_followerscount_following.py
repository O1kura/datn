# Generated by Django 4.2.11 on 2024-05-29 18:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0011_remove_comment_name_comment_author"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="followerscount",
            name="user",
        ),
        migrations.AddField(
            model_name="followerscount",
            name="following",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="following_set",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
