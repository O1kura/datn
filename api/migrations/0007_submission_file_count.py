# Generated by Django 4.2.11 on 2024-04-21 17:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0006_alter_questiondata_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="file_count",
            field=models.IntegerField(default=0),
        ),
    ]
