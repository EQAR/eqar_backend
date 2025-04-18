# Generated by Django 4.2.19 on 2025-03-16 00:53

from django.db import migrations
from django.conf import settings

from eqar_backend.meilisearch import MeiliClient

def configure_index(apps, schema_editor):
    if hasattr(settings, "MEILI_API_URL"):
        meili = MeiliClient()
        meili.wait_for(meili.update_settings(meili.INDEX_INSTITUTIONS, {
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
                'deqar_id',
                'eter_id',
            ],
            'sortableAttributes': [
                'name_sort',
                'locations.country.name_english',
                'founding_date',
                'closure_date',
                'deqar_id',
                'eter_id',
            ],
        }))


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0037_delete_institutioneterrecord'),
    ]

    operations = [
        migrations.RunPython(configure_index, reverse_code=migrations.RunPython.noop),
    ]
