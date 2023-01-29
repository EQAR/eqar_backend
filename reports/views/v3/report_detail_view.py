from rest_framework import generics

from reports.models import Report
from reports.serializers.v3.report_detail_serializer import ReportDetailSerializer


class ReportDetailView(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected institution.
    """
    serializer_class = ReportDetailSerializer
    queryset = Report.objects.all()