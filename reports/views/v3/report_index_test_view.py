from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.response import Response

from reports.indexers.reports_v3_indexer import ReportsIndexerV3


class ReportIndexTestView(generics.RetrieveAPIView):
    """
        Returns report solr document.
    """
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        try:
            indexer = ReportsIndexerV3(report_id=pk)
            indexer.create_solr_document()
            return Response(indexer.get_solr_document())
        except ObjectDoesNotExist:
            return Response(status=404)
