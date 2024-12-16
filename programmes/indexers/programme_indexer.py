from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured

import meilisearch

from programmes.models import Programme

from programmes.serializers.programme_indexer_serializer import ProgrammeIndexerSerializer


class ProgrammeIndexer:
    """
    Index Programme with Meilisearch
    """
    serializer = ProgrammeIndexerSerializer

    def __init__(self):
        if hasattr(settings, "MEILI_API_URL"):
            meili_url = getattr(settings, "MEILI_API_URL")
            meili_key = getattr(settings, "MEILI_API_KEY", None)
            self.meili_index = getattr(settings, "MEILI_INDEX_PROGRAMMES", 'programmes-v3')
            self.meili = meilisearch.Client(meili_url, meili_key)
        else:
            raise ImproperlyConfigured("Meilisearch not configured")

    def index(self, programme_id):
        programme = Programme.objects.get(pk=programme_id)
        doc = self.serializer(programme).data
        self.meili.index(self.meili_index).add_documents(doc)

    def delete(self, programme_id):
        self.meili.index(self.meili_index).delete_document(programme_id)

