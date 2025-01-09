# create reports index

from django.db import migrations
from django.conf import settings

from eqar_backend.meilisearch import MeiliClient

import time

def configure_index(apps, schema_editor):
    if hasattr(settings, "MEILI_API_URL"):
        meili = MeiliClient()
        meili.create_index(meili.INDEX_INSTITUTIONS, { 'primaryKey': 'id' })
        meili.update_settings(meili.INDEX_INSTITUTIONS, {
            'displayedAttributes': [ '*' ],
            'searchableAttributes': [
                'name_primary',
                'names.acronym',
                'names.name_official',
                'names.name_official_transliterated',
                'names.name_english',
                'names.name_versions.name',
                'names.name_versions.transliteration',
                'locations.city',
                'locations.country.name_english',
                'website_link',
            ],
            'filterableAttributes': [
                'is_other_provider',
                'organization_type',
                'locations.country.id',
                'locations.country_verified',
                'locations.lat',
                'locations.long',
                'qf_ehea_levels',
                'founding_date',
                'closure_date',
                'has_report',
                'agencies.id',
                'activity_types',
                'crossborder',
                'status',
            ],
            'sortableAttributes': [
                'name_sort',
                'locations.country.name_english',
                'founding_date',
                'closure_date',
            ],
            'faceting': {
                'maxValuesPerFacet': 200,
            },
            'pagination': {
                'maxTotalHits': 200000,
            },
        })


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0035_auto_20240207_2139'),
    ]

    operations = [
        migrations.RunPython(configure_index, reverse_code=migrations.RunPython.noop),
    ]
