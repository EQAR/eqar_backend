# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-15 17:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submissionapi', '0004_auto_20180315_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionpackagelog',
            name='submission_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
