from django.conf import settings
from django.db.models import Q

import meilisearch

from programmes.models import Programme

from programmes.serializers.programme_indexer_serializer import ProgrammeIndexerSerializer


class ProgrammeIndexer:
    """
    Index Programme with Meilisearch
    """
    meili_index = 'programmes-v3'
    serializer = ProgrammeIndexerSerializer

    def __init__(self, programme_id):
        self.programme = Programme.objects.get(pk=programme_id)
        meili_url = getattr(settings, "MEILI_API_URL", "http://meili:7700")
        meili_key = getattr(settings, "MEILI_API_KEY", None)
        self.meili = meilisearch.Client(meili_url, meili_key)

    def index(self):
        doc = self.serializer(self.programme).data
        self.meili.index(self.meili_index).add_documents(doc)

