# Generated by Django 4.2.19 on 2025-03-29 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0035_meili_add_activity_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='name',
        ),
    ]
