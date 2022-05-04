from drf_rw_serializers import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from ipware import get_client_ip
from submissionapi.tasks import recheck_flag
from reports.tasks import index_delete_report

from adminapi.permissions import CanEditReport
from adminapi.serializers.report_serializers import ReportReadSerializer, ReportWriteSerializer
from lists.models import Flag
from reports.models import Report, ReportUpdateLog, ReportFlag
from submissionapi.flaggers.report_flagger import ReportFlagger
from submissionapi.trackers.submission_tracker import SubmissionTracker


class ReportFlagCheck(generics.CreateAPIView):
    queryset = Report.objects.all()
    write_serializer_class = ReportWriteSerializer

    def create(self, request, *args, **kwargs):
        pass


class ReportCreate(generics.CreateAPIView):
    queryset = Report.objects.all()
    read_serializer_class = ReportReadSerializer
    write_serializer_class = ReportWriteSerializer

    def perform_create(self, serializer):
        report = serializer.save(created_by=self.request.user)
        report.name = report.agency_esg_activity.activity + ' (by ' + report.agency.acronym_primary + ')'
        report.save()
        flagger = ReportFlagger(report=report)
        flagger.check_and_set_flags()
        client_ip, is_routable = get_client_ip(self.request)
        tracker = SubmissionTracker(original_data=self.request.data,
                                    origin='form',
                                    user_profile=self.request.user.deqarprofile,
                                    ip_address=client_ip)
        tracker.log_package()


class ReportDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Report.objects.all()
    read_serializer_class = ReportReadSerializer
    write_serializer_class = ReportWriteSerializer
    permission_classes = (CanEditReport|IsAdminUser,)

    @swagger_auto_schema(responses={'200': ReportReadSerializer})
    def get(self, request, *args, **kwargs):
        return super(ReportDetail, self).get(request, *args, **kwargs)

    @swagger_auto_schema(request_body=ReportWriteSerializer, responses={'200': ReportReadSerializer})
    def put(self, request, *args, **kwargs):
        return super(ReportDetail, self).put(request, *args, **kwargs)

    def perform_update(self, serializer):
        report = serializer.save()
        flagger = ReportFlagger(report=report)
        flagger.check_and_set_flags()

        submit_comment = self.request.data.get('submit_comment', None)
        if submit_comment:
            ReportUpdateLog.objects.create(
                report=report,
                note=submit_comment,
                updated_by=self.request.user
            )
        else:
            ReportUpdateLog.objects.create(
                report=report,
                note='Report updated',
                updated_by=self.request.user
            )

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
        report_flagger = ReportFlagger(report=report)
        report_flagger.set_flag()
        index_delete_report.delay(report.id)
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

        # Reindex and recheck flag
        recheck_flag(report=report_flag.report)

        return Response(data={'OK'}, status=200)
