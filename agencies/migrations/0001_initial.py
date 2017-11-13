# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-12 19:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lists', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('eqar_id', models.CharField(max_length=25)),
                ('contact_person', models.CharField(max_length=150)),
                ('fax', models.CharField(blank=True, max_length=20)),
                ('website_link', models.URLField(max_length=100)),
                ('specialisation_note', models.TextField(blank=True)),
                ('activity_note', models.TextField(blank=True)),
                ('reports_link', models.URLField()),
                ('description_note', models.TextField()),
                ('registration_start', models.DateField()),
                ('registration_valid_to', models.DateField()),
                ('registration_note', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'eqar_agencies',
            },
        ),
        migrations.CreateModel(
            name='AgencyActivityType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'eqar_agency_activity_types',
            },
        ),
        migrations.CreateModel(
            name='AgencyEmail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=50)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
            ],
            options={
                'db_table': 'eqar_agency_emails',
            },
        ),
        migrations.CreateModel(
            name='AgencyENQUAMembership',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('membership', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'eqar_agency_enqua_memberships',
            },
        ),
        migrations.CreateModel(
            name='AgencyEQARChange',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('change_date', models.DateField()),
                ('change_report_file', models.FileField(upload_to='')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
            ],
            options={
                'db_table': 'eqar_agency_eqar_changes',
            },
        ),
        migrations.CreateModel(
            name='AgencyEQARRenewal',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('renewal_date', models.DateField()),
                ('review_report_file', models.FileField(blank=True, upload_to='')),
                ('decision_file', models.FileField(blank=True, upload_to='')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
            ],
            options={
                'db_table': 'eqar_agency_eqar_renewals',
            },
        ),
        migrations.CreateModel(
            name='AgencyESGActivities',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('activity_description', models.CharField(blank=True, max_length=300)),
                ('esg_activity', models.CharField(max_length=200)),
                ('activity_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.AgencyActivityType')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
            ],
            options={
                'db_table': 'eqar_agency_esga_activities',
            },
        ),
        migrations.CreateModel(
            name='AgencyFocus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('focus', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'eqar_agency_focuses',
            },
        ),
        migrations.CreateModel(
            name='AgencyFocusCountry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('focus_country_official', models.BooleanField(default=False)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lists.Country')),
            ],
            options={
                'db_table': 'eqar_agency_focus_countries',
            },
        ),
        migrations.CreateModel(
            name='AgencyHistoricalData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.CharField(max_length=200)),
                ('valid_from', models.DateField(blank=True, null=True)),
                ('valid_to', models.DateField(blank=True, null=True)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
            ],
            options={
                'db_table': 'eqar_agecy_historical_data',
            },
        ),
        migrations.CreateModel(
            name='AgencyHistoricalField',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('field', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'eqar_agency_historical_fields',
            },
        ),
        migrations.CreateModel(
            name='AgencyLevels',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
                ('qf_ehea_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lists.QFEHEALevel')),
            ],
            options={
                'db_table': 'eqar_agency_levels',
            },
        ),
        migrations.CreateModel(
            name='AgencyLocationCountry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lists.Country')),
            ],
            options={
                'db_table': 'eqar_agency_location_countries',
            },
        ),
        migrations.CreateModel(
            name='AgencyMembership',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
                ('associaton', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lists.Association')),
            ],
            options={
                'db_table': 'eqar_agency_memberships',
            },
        ),
        migrations.CreateModel(
            name='AgencyName',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name_note', models.TextField(blank=True)),
                ('valid_to', models.DateField(blank=True, null=True)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
            ],
            options={
                'db_table': 'eqar_agency_names',
            },
        ),
        migrations.CreateModel(
            name='AgencyNameVersion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('name_transliterated', models.CharField(blank=True, max_length=200)),
                ('name_is_primary', models.BooleanField(default=False)),
                ('acronym', models.CharField(blank=True, max_length=20)),
                ('acronym_transliterated', models.CharField(blank=True, max_length=20)),
                ('acronym_is_primary', models.BooleanField(default=False)),
                ('agency_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.AgencyName')),
            ],
            options={
                'db_table': 'eqar_agency_name_versions',
            },
        ),
        migrations.CreateModel(
            name='AgencyPhone',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('phone', models.CharField(max_length=20)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency')),
            ],
            options={
                'db_table': 'eqar_agency_phones',
            },
        ),
        migrations.CreateModel(
            name='AgencyRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField()),
                ('date', models.DateField()),
                ('from_agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_agencies', to='agencies.Agency')),
                ('to_agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_agencies', to='agencies.Agency')),
            ],
            options={
                'db_table': 'eqar_agency_relationships',
            },
        ),
        migrations.AddField(
            model_name='agencyhistoricaldata',
            name='field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.AgencyHistoricalField'),
        ),
        migrations.AddField(
            model_name='agency',
            name='enqua_membership',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agencies.AgencyENQUAMembership'),
        ),
        migrations.AddField(
            model_name='agency',
            name='focus',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='agencies.AgencyFocus'),
        ),
        migrations.AddField(
            model_name='agency',
            name='related_agencies',
            field=models.ManyToManyField(through='agencies.AgencyRelationship', to='agencies.Agency'),
        ),
        migrations.AlterUniqueTogether(
            name='agencyrelationship',
            unique_together=set([('from_agency', 'to_agency')]),
        ),
    ]
