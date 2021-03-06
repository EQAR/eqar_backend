# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-05 20:09
from __future__ import unicode_literals

from django.db import migrations, models
import reports.models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0008_auto_20180222_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportfile',
            name='file',
            field=models.FileField(blank=True, max_length=255, upload_to=reports.models.set_directory_path),
        ),
        migrations.AlterField(
            model_name='reportlink',
            name='link',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]
