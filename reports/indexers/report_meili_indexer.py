from django.conf import settings

from eqar_backend.meilisearch import MeiliIndexer

from reports.models import Report

from reports.serializers.report_meili_indexer_serializer import ReportIndexerSerializer

class ReportIndexer(MeiliIndexer):
    """
    Index Report with Meilisearch
    """
    serializer = ReportIndexerSerializer
    model = Report

