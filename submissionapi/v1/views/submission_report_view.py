from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from ipware import get_client_ip
from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from adminapi.permissions import CanEditReport
from institutions.models import Institution
from lists.models import Flag
from reports.models import Report, ReportFlag, ReportUpdateLog
from submissionapi.flaggers.report_flagger import ReportFlagger
from submissionapi.populators.populator import Populator
from submissionapi.v1.serializers.response_serializers import ResponseReportSerializer, \
    ResponseReportSuccessResponseSerializer, ResponseReportErrorResponseSerializer
from submissionapi.v1.serializers.submisson_serializers import SubmissionPackageSerializer
from submissionapi.trackers.submission_tracker import SubmissionTracker
from submissionapi.tasks import send_submission_email


class SubmissionReportView(APIView):
    """
        Submission of report data
    """
    @swagger_auto_schema(request_body=SubmissionPackageSerializer,
                         responses={'200': ResponseReportSuccessResponseSerializer,
                                    '201': None,
                                    '400': ResponseReportErrorResponseSerializer})
    def post(self, request):
        # Save the highest institution id
        try:
            max_inst = Institution.objects.latest('id').id
        except ObjectDoesNotExist:
            max_inst = 0

        # Tracking
        http_origin = request.META.get('HTTP_ORIGIN', None)
        if http_origin:
            if 'deqar.eu' in http_origin:
                origin = 'form'
            else:
                origin = 'api'
        else:
            origin = 'api'

        client_ip, is_routable = get_client_ip(request)
        tracker = SubmissionTracker(original_data=request.data,
                                    origin=origin,
                                    user_profile=request.user.deqarprofile,
                                    ip_address=client_ip)
        tracker.log_package()

        # Check if request is a list:
        if isinstance(request.data, list):
            submitted_reports = []
            accepted_reports = []
            response_contains_success = False
            response_contains_error = False

            for data in request.data:
                serializer = SubmissionPackageSerializer(data=data, context={'request': request})
                if serializer.is_valid():
                    populator = Populator(data=serializer.validated_data, user=request.user)
                    populator.populate()
                    flagger = ReportFlagger(report=populator.report)
                    flagger.check_and_set_flags()
                    tracker.log_report(populator, flagger)
                    submitted_reports.append(self.make_success_response(populator, flagger))
                    accepted_reports.append(self.make_success_response(populator, flagger))
                    response_contains_success = True

                    # Add log entry
                    ReportUpdateLog.objects.create(
                        report=populator.report,
                        note="Report updated via API.",
                        updated_by=request.user
                    )

                else:
                    submitted_reports.append(self.make_error_response(serializer, data))
                    response_contains_error = True

            if response_contains_success:
                send_submission_email.delay(response=accepted_reports,
                                            institution_id_max=max_inst,
                                            total_submission=len(submitted_reports),
                                            agency_email=request.user.email)

            if response_contains_error:
                return Response(submitted_reports, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(submitted_reports, status=status.HTTP_200_OK)

        # If request is not a list
        else:
            serializer = SubmissionPackageSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                populator = Populator(data=serializer.validated_data, user=request.user)
                populator.populate()
                flagger = ReportFlagger(report=populator.report)
                flagger.check_and_set_flags()
                tracker.log_report(populator, flagger)

                send_submission_email.delay(response=[self.make_success_response(populator, flagger)],
                                            institution_id_max=max_inst,
                                            total_submission=1,
                                            agency_email=request.user.email)

                # Add log entry
                ReportUpdateLog.objects.create(
                    report=populator.report,
                    note="Report updated via API.",
                    updated_by=request.user
                )
                return Response(self.make_success_response(populator, flagger), status=status.HTTP_200_OK)
            else:
                return Response(self.make_error_response(serializer, request.data), status=status.HTTP_400_BAD_REQUEST)

    def make_success_response(self, populator, flagger):
        institution_warnings = populator.institution_flag_log
        report_warnings = [fl.flag_message for fl in flagger.report.reportflag_set.filter(active=True)]

        if len(institution_warnings) > 0 or len(report_warnings) > 0:
            sanity_check_status = "warnings"
        else:
            sanity_check_status = "success"

        serializer = ResponseReportSerializer(flagger.report)

        return {
            'submission_status': 'success',
            'submitted_report': serializer.data,
            'sanity_check_status': sanity_check_status,
            'report_flag': flagger.report.flag.flag,
            'report_warnings': report_warnings,
            'institution_warnings': institution_warnings
        }

    def make_error_response(self, serializer, original_data):
        return {
            'submission_status': 'errors',
            'original_data': original_data,
            'errors': serializer.errors
        }


class ReportDelete(APIView):
    """
        Requests report records to be not visible on the public and on the search interface.
    """
    permission_classes = (CanEditReport|IsAdminUser,)

    @swagger_auto_schema(responses={'200': 'OK'})
    def delete(self, request, *args, **kwargs):
        report = get_object_or_404(Report, id=kwargs.get('pk'))
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
