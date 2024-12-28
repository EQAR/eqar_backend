from django.db import migrations
from django.conf import settings

from eqar_backend.meilisearch import MeiliClient

def update_index(apps, schema_editor):
    if hasattr(settings, "MEILI_API_URL"):
        meili = MeiliClient()
        meili.update_settings(meili.INDEX_PROGRAMMES, {
            'pagination': {
                'maxTotalHits': 3000,
            },
        })


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0024_update_meilisearch'),
    ]

    operations = [
        migrations.RunPython(update_index, reverse_code=migrations.RunPython.noop),
    ]
