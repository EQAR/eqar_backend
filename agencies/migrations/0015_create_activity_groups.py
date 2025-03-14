# Generated by Django 4.2.19 on 2025-03-08 18:48
import csv
import os

from celery.bin.celery import report
from django.db import migrations

def load_csv_data(apps, schema_editor):
    activity_groups = {}
    reports_links = {}

    # Get the models
    AgencyESGActivity = apps.get_model('agencies', 'AgencyESGActivity')
    AgencyActivityGroup = apps.get_model('agencies', 'AgencyActivityGroup')

    # Get the migration file path
    migration_dir = os.path.dirname(__file__)  # Directory of the migration file
    csv_path = os.path.join(migration_dir, 'csv', 'DEQARActivityGroups.csv')

    # Read the CSV and create a dictionary with the group names
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            activity_groups[row['activity_id']] = row['group_name']
            activity_groups[row['activity_id']] = row['reports_link']

    for activity in AgencyESGActivity.objects.all():
        activity_group = activity_groups.get(activity.id)
        reports_link = reports_links.get(activity.id)

        if activity_group:
            group, created = AgencyActivityGroup.objects.get_or_create(
                activity=activity_group,
                activity_type=activity.activity_type,
            )
            if reports_link:
                group.reports_link = reports_link
                group.save()

        else:
            group = AgencyActivityGroup.objects.create(
                activity=activity_group,
                activity_type=activity.activity_type
            )

        activity.activity_group = group
        activity.save()

class Migration(migrations.Migration):

    dependencies = [
        ('agencies', '0014_agencyactivitygroup_agencyesgactivity_activity_group'),
    ]

    operations = [
        migrations.RunPython(load_csv_data),
    ]
