# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-10 19:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0005_auto_20180110_1928'),
        ('institutions', '0004_auto_20180108_1831'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='institutioncountry',
            name='country',
        ),
        migrations.RemoveField(
            model_name='institutioncountry',
            name='institution',
        ),
        migrations.AddField(
            model_name='institution',
            name='countries',
            field=models.ManyToManyField(to='countries.Country'),
        ),
        migrations.DeleteModel(
            name='InstitutionCountry',
        ),
    ]
