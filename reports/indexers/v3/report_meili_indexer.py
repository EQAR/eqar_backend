from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured

import meilisearch

from reports.models import Report

from reports.serializers.v3.report_meili_indexer_serializer import ReportIndexerSerializer


class ReportIndexer:
    """
    Index Report with Meilisearch
    """
    serializer = ReportIndexerSerializer

    def __init__(self, report_id):
        if hasattr(settings, "MEILI_API_URL"):
            meili_url = getattr(settings, "MEILI_API_URL")
            meili_key = getattr(settings, "MEILI_API_KEY", None)
            self.meili_index = getattr(settings, "MEILI_INDEX_REPORTS", 'reports-v3')
            self.meili = meilisearch.Client(meili_url, meili_key)
        else:
            raise ImproperlyConfigured("Meilisearch not configured")
        self.report = Report.objects.get(pk=report_id)

    def index(self):
        doc = self.serializer(self.report).data
        self.meili.index(self.meili_index).add_documents(doc)

