# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-05 15:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0008_auto_20180406_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institutioncountry',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
