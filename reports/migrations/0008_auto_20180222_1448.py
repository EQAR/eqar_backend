# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-22 14:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0007_auto_20180221_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportfile',
            name='file_display_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='reportfile',
            name='file_original_location',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
