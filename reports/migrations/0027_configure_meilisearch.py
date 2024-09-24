# create reports index

from django.db import migrations
from django.conf import settings

import meilisearch

import time

def configure_index(apps, schema_editor):
    if hasattr(settings, "MEILI_API_URL"):
        url = getattr(settings, "MEILI_API_URL")
        key = getattr(settings, "MEILI_API_KEY", None)
        index = getattr(settings, "MEILI_INDEX_REPORTS", 'reports-v3')
        meili = meilisearch.Client(url, key)
        task_create = meili.create_index(index, { 'primaryKey': 'id' })
        meili.index(index).update_settings({
            'displayedAttributes': [ '*' ],
            'searchableAttributes': [
                'institutions.name_sort',
                'institutions.name_primary',
                'institutions.locations.city',
                'programmes.names.name',
                'programmes.names.qualification'
            ],
            'filterableAttributes': [
                'agency',
                'agency_esg_activity.id',
                'agency_esg_activity.type',
                'crossborder',
                'decision',
                'status',
                'valid_from',
                'valid_to_calculated',
                'created_at',
                'updated_at',
                'report_files.languages',
                'institutions.id',
                'institutions.locations.country',
                'programmes.degree_outcome',
                'programmes.qf_ehea_level',
                'programmes.programme_type',
                'programmes.workload_ects',
                'other_provider_covered',
                'flag_level'
            ],
            'sortableAttributes': [
                'created_at',
                'updated_at',
                'valid_from',
                'valid_to_calculated',
                'institutions.name_sort',
            ],
        })


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0026_remove_report_micro_credentials_covered'),
    ]

    operations = [
        migrations.RunPython(configure_index, reverse_code=migrations.RunPython.noop),
    ]
