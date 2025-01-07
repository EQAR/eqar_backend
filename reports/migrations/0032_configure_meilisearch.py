# update reports index settings

from django.db import migrations
from django.conf import settings

from eqar_backend.meilisearch import MeiliClient

import time

def configure_index(apps, schema_editor):
    if hasattr(settings, "MEILI_API_URL"):
        meili = MeiliClient()
        meili.update_settings(meili.INDEX_REPORTS, {
            'filterableAttributes': [
                'agency.id',
                'contributing_agencies.id',
                'agency_esg_activities.id',
                'agency_esg_activities.type',
                'crossborder',
                'decision',
                'status',
                'valid_from',
                'valid_to_calculated',
                'created_at',
                'updated_at',
                'report_files.languages',
                'institutions.id',
                'institutions.locations.country.id',
                'institutions.locations.country.iso_3166_alpha2',
                'institutions.locations.country.iso_3166_alpha3',
                'institutions.locations.country.ehea_is_member',
                'programmes.degree_outcome',
                'programmes.qf_ehea_level',
                'programmes.programme_type',
                'programmes.workload_ects',
                'other_provider_covered',
                'flag',
            ],
            'sortableAttributes': [
                'created_at',
                'updated_at',
                'valid_from',
                'valid_to_calculated',
                'institutions.name_sort',
                'institutions.locations.country.name_english',
                'agency.acronym_primary',
                'agency_esg_activities.type',
                'flag',
            ],
        })


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0031_auto_20250103_2024'),
    ]

    operations = [
        migrations.RunPython(configure_index, reverse_code=migrations.RunPython.noop),
    ]

