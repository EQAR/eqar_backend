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
