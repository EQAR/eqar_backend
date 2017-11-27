# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-26 17:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0002_programme_report'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programme',
            name='nqf_level',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='programme',
            name='qf_ehea_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lists.QFEHEALevel'),
        ),
    ]