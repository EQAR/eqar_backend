# Generated by Django 4.2.19 on 2025-03-08 18:48
import yaml
import os

import logging

from django.db import migrations

from django.core.management import call_command

def create_groups(apps, schema_editor):
    logger = logging.getLogger('django')

    # Get the models
    AgencyESGActivity = apps.get_model('agencies', 'AgencyESGActivity')
    AgencyActivityGroup = apps.get_model('agencies', 'AgencyActivityGroup')

    # Get the migration file path
    migration_dir = os.path.dirname(__file__)  # Directory of the migration file
    yaml_path = os.path.join(migration_dir, 'data', 'DEQARActivityGroups.yaml')

    # Read the data file
    with open(yaml_path, encoding='utf-8') as datafile:
        activity_groups = yaml.safe_load(datafile)

    # Make sure activity types are known
    call_command('loaddata', '--ignorenonexistent', 'agency_activity_type')

    # Step 1: pre-group activities per data file
    for group_def in activity_groups:
        # create group
        kwargs = {
            'activity': group_def['group_name'],
            'activity_type_id': group_def['activity_type'],
        }
        if 'id' in group_def:
            kwargs['id'] = group_def['id']
        if 'reports_link' in group_def:
            kwargs['reports_link'] = group_def['reports_link']
        group = AgencyActivityGroup.objects.create(**kwargs)
        # assign listed activities to this group
        for activity_id in group_def['activities']:
            try:
                activity = AgencyESGActivity.objects.get(id=activity_id)
                if activity.activity_type != group.activity_type:
                    logger.warning(f'  - warning: activity group [{group.activity}] with type [{group.activity_type.type}] includes inconsistent activity [{activity.activity}] of [{activity.agency.acronym_primary}] with type [{activity.activity_type.type}]')
                activity.activity_group = group
                activity.save()
            except AgencyESGActivity.DoesNotExist:
                logger.warning(f'  - warning: activity group [{group.activity}] includes unknown ID [{activity_id}]')

    # Step 2: make each other activity a group on its own
    for activity in AgencyESGActivity.objects.filter(activity_group__isnull=True):
        group = AgencyActivityGroup.objects.create(
            activity=activity.activity,
            activity_type=activity.activity_type,
            reports_link=activity.reports_link,
        )
        activity.activity_group = group
        activity.save()

class Migration(migrations.Migration):

    dependencies = [
        ('agencies', '0014_agencyactivitygroup_agencyesgactivity_activity_group'),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
