
from django.db import migrations
from django.conf import settings

import meilisearch

def update_index(apps, schema_editor):
    if hasattr(settings, "MEILI_API_URL"):
        url = getattr(settings, "MEILI_API_URL")
        key = getattr(settings, "MEILI_API_KEY", None)
        index = getattr(settings, "MEILI_INDEX_PROGRAMMES", 'programmes-v3')
        meili = meilisearch.Client(url, key)
        meili.index(index).update_settings({
            'filterableAttributes': [
                'degree_outcome',
                'programme_type',
                'institutions',
                'qf_ehea_level',
                'report.agency',
                'report.crossborder',
                'report.decision',
                'report.agency_esg_activity.id',
                'report.agency_esg_activity.type',
                'report.status',
                'report.valid_from',
                'report.valid_to_calculated',
                'report.created_at',
                'report.updated_at',
                'report.report_files.languages',
                'workload_ects',
            ],
            'sortableAttributes': [
                'name_primary',
                'report.valid_from',
                'report.valid_to_calculated',
                'report.created_at',
                'report.updated_at',
            ],
        })


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0023_update_meilisearch'),
    ]

    operations = [
        migrations.RunPython(update_index, reverse_code=migrations.RunPython.noop),
    ]
