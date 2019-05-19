from django.utils import timezone
from drf_rw_serializers import generics

from adminapi.serializers.report_serializers import ReportReadSerializer, ReportWriteSerializer
from reports.models import Report


class ReportDetail(generics.RetrieveUpdateAPIView):
    queryset = Report.objects.all()
    read_serializer_class = ReportReadSerializer
    write_serializer_class = ReportWriteSerializer

    def update(self, request, *args, **kwargs):
        report = Report.objects.get(id=kwargs.get('pk'))
        report.updated_by = request.user
        report.updated_at = timezone.now()
        report.save()
        return super(ReportDetail, self).update(request, *args, **kwargs)