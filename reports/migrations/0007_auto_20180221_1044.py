# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-21 10:44
from __future__ import unicode_literals

from django.db import migrations, models
import reports.models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0006_auto_20180220_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportfile',
            name='file',
            field=models.FileField(blank=True, upload_to=reports.models.set_directory_path),
        ),
    ]