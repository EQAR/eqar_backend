from django.conf import settings

from eqar_backend.meilisearch import MeiliClient

from programmes.models import Programme

from programmes.serializers.programme_indexer_serializer import ProgrammeIndexerSerializer


class ProgrammeIndexer:
    """
    Index Programme with Meilisearch
    """
    serializer = ProgrammeIndexerSerializer

    def __init__(self):
        self.meili = MeiliClient()

    def index(self, programme_id):
        programme = Programme.objects.get(pk=programme_id)
        doc = self.serializer(programme).data
        self.meili.add_document(self.meili.INDEX_PROGRAMMES, doc)

    def delete(self, programme_id):
        self.meili.delete_document(self.meili.INDEX_PROGRAMMES, programme_id)

