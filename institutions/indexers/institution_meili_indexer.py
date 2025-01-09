from django.conf import settings

from eqar_backend.meilisearch import MeiliIndexer, MeiliClient

from institutions.models import Institution

from institutions.serializers.institution_indexer_serializer import InstitutionIndexerSerializer

class InstitutionIndexer(MeiliIndexer):
    """
    Index Institution with Meilisearch
    """
    serializer = InstitutionIndexerSerializer
    model = Institution

