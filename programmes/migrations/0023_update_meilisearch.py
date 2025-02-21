from django.db import migrations
from django.conf import settings

from eqar_backend.meilisearch import MeiliClient

def update_index(apps, schema_editor):
    if hasattr(settings, "MEILI_API_URL"):
        meili = MeiliClient()
        meili.wait_for(meili.update_settings(meili.INDEX_PROGRAMMES, {
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
                'report.report_files.languages',
                'workload_ects'
            ],
        }))


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0022_configure_meilisearch'),
    ]

    operations = [
        migrations.RunPython(update_index, reverse_code=migrations.RunPython.noop),
    ]
