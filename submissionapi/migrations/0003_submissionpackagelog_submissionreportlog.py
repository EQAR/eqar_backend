# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-15 09:55
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agencies', '0003_agency_flag_log'),
        ('accounts', '0001_initial'),
        ('reports', '0009_auto_20180305_2009'),
        ('submissionapi', '0002_auto_20180219_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubmissionPackageLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('origin', models.CharField(blank=True, max_length=10, null=True)),
                ('submitted_data', models.TextField(blank=True)),
                ('submission_date', models.DateField(default=datetime.date.today)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.DEQARProfile')),
            ],
            options={
                'db_table': 'deqar_submission_package_log',
            },
        ),
        migrations.CreateModel(
            name='SubmissionReportLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('report_status', models.CharField(default='success', max_length=20)),
                ('report_warnings', models.TextField(blank=True)),
                ('institution_warnings', models.TextField(blank=True)),
                ('country_warnings', models.TextField(blank=True)),
                ('submission_date', models.DateField(default=datetime.date.today)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Report')),
            ],
            options={
                'db_table': 'deqar_submission_report_log',
            },
        ),
    ]