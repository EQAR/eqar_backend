# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-15 18:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('submissionapi', '0005_auto_20180315_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionreportlog',
            name='submission_package_log',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='submissionapi.SubmissionPackageLog'),
            preserve_default=False,
        ),
    ]
