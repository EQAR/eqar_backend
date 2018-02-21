# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-18 16:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0004_auto_20180217_0937'),
    ]

    operations = [
        migrations.AddField(
            model_name='institutioncountry',
            name='country_verified',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='institutionqfehealevel',
            name='qf_ehea_level_verified',
            field=models.BooleanField(default=True),
        ),
    ]