from django.utils import timezone
from drf_rw_serializers import generics
from drf_yasg.utils import swagger_auto_schema

from adminapi.serializers.report_serializers import ReportReadSerializer, ReportWriteSerializer
from reports.models import Report, ReportUpdateLog


class ReportDetail(generics.RetrieveUpdateAPIView):
    queryset = Report.objects.all()
    read_serializer_class = ReportReadSerializer
    write_serializer_class = ReportWriteSerializer

    @swagger_auto_schema(responses={'200': ReportReadSerializer})
    def get(self, request, *args, **kwargs):
        return super(ReportDetail, self).get(request, *args, **kwargs)

    @swagger_auto_schema(request_body=ReportWriteSerializer, responses={'200': ReportReadSerializer})
    def put(self, request, *args, **kwargs):
        report = Report.objects.get(id=kwargs.get('pk'))

        submit_comment = request.data.get('submit_comment', None)
        if submit_comment:
            ReportUpdateLog.objects.create(
                report=report,
                note=submit_comment,
                updated_by=request.user
            )

        report.save()
        return super(ReportDetail, self).put(request, *args, **kwargs)