# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-14 11:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0003_auto_20180207_2020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programmeidentifier',
            name='resource',
            field=models.CharField(blank=True, default='local identifier', max_length=30),
        ),
    ]
