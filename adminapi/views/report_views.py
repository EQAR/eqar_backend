from drf_rw_serializers import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from adminapi.permissions import CanEditReport
from adminapi.serializers.report_serializers import ReportReadSerializer, ReportWriteSerializer
from lists.models import Flag
from reports.models import Report, ReportUpdateLog, ReportFlag


class ReportDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Report.objects.all()
    read_serializer_class = ReportReadSerializer
    write_serializer_class = ReportWriteSerializer
    permission_classes = (CanEditReport,)

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

    @swagger_auto_schema(responses={'200': 'OK'})
    def delete(self, request, *args, **kwargs):
        report = Report.objects.get(id=kwargs.get('pk'))
        flag = Flag.objects.get(flag='high level')
        report_flag, created = ReportFlag.objects.get_or_create(
            report=report,
            flag=flag,
            flag_message='Deletion was requested.',
        )
        if created or report_flag.active is False:
            ReportUpdateLog.objects.create(
                report=report,
                note='Deletion flag was assigned.',
                updated_by=request.user
            )
            report_flag.active = True
            report_flag.removed_by_eqar = False
            report_flag.save()
        return Response(data={'OK'}, status=200)


class ReportFlagRemove(APIView):
    permission_classes = (IsAdminUser,)

    @swagger_auto_schema(responses={'200': 'OK'})
    def delete(self, request, *args, **kwargs):
        report_flag = ReportFlag.objects.get(id=kwargs.get('pk'))
        report_flag.active = False
        report_flag.removed_by_eqar = True
        report_flag.save()
        ReportUpdateLog.objects.get_or_create(
            report=report_flag.report,
            note='%s flag was removed' % report_flag.flag.flag.title(),
            updated_by=request.user
        )
        return Response(data={'OK'}, status=200)
