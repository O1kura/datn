# Generated by Django 4.2.11 on 2024-04-09 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_data_value_remove_question_box_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='symbol_box',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
