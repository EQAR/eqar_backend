from rest_framework import generics

from adminapi.serializers.report_serializers import ReportSerializer
from reports.models import Report


class ReportDetail(generics.RetrieveUpdateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

