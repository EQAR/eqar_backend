from django.conf import settings

from eqar_backend.meilisearch import MeiliIndexer

from programmes.models import Programme

from programmes.serializers.programme_indexer_serializer import ProgrammeIndexerSerializer


class ProgrammeIndexer(MeiliIndexer):
    """
    Index Programme with Meilisearch
    """
    serializer = ProgrammeIndexerSerializer
    model = Programme

