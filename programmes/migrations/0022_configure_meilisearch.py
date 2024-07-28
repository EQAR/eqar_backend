# Generated by Django 2.2.28 on 2024-07-28 20:36

from django.db import migrations
from django.conf import settings

import meilisearch

def configure_index(apps, schema_editor):
    if hasattr(settings, "MEILI_API_URL"):
        url = getattr(settings, "MEILI_API_URL")
        key = getattr(settings, "MEILI_API_KEY", None)
        index = getattr(settings, "MEILI_INDEX_PROGRAMMES", 'programmes-v3')
        meili = meilisearch.Client(url, key)
        meili.create_index(index, { 'primaryKey': 'id' })
        meili.index(index).update_settings({
            'displayedAttributes': [ '*' ],
            'searchableAttributes': [
                'names.name',
                'names.qualification'
            ],
            'filterableAttributes': [
                'degree_outcome',
                'programme_type',
                'institutions',
                'qf_ehea_level',
                'report.agency',
                'report.crossborder',
                'report.decision',
                'report.status',
                'report.valid_from',
                'report.valid_to',
                'workload_ects'
            ],
            'sortableAttributes': [
                'name_primary',
                'report.valid_from',
                'report.valid_to',
            ],
        })


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0021_auto_20231107_2216'),
    ]

    operations = [
        migrations.RunPython(configure_index, reverse_code=migrations.RunPython.noop),
    ]
