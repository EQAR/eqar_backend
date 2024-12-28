from django.conf import settings

from eqar_backend.meilisearch import MeiliClient

from reports.models import Report

from reports.serializers.v3.report_meili_indexer_serializer import ReportIndexerSerializer

class ReportIndexer:
    """
    Index Report with Meilisearch
    """
    serializer = ReportIndexerSerializer

    def __init__(self):
        self.meili = MeiliClient()

    def index(self, report_id):
        report = Report.objects.get(pk=report_id)
        doc = self.serializer(report).data
        self.meili.add_document(self.meili.INDEX_REPORTS, doc)

    def delete(self, report_id):
        self.meili.delete_document(self.meili.INDEX_REPORTS, report_id)

