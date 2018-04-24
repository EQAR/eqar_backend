import io
from django.core.exceptions import ObjectDoesNotExist
from ipware import get_client_ip
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from institutions.models import Institution
from submissionapi.csv_functions.csv_handler import CSVHandler
from submissionapi.csv_functions.csv_parser import CSVParser
from submissionapi.flaggers.report_flagger import ReportFlagger
from submissionapi.populators.populator import Populator
from submissionapi.serializers.response_serializers import ReportResponseSerializer
from submissionapi.serializers.submisson_serializers import SubmissionPackageSerializer
from submissionapi.tasks import send_submission_email
from submissionapi.trackers.submission_tracker import SubmissionTracker


class SubmissionCSVView(APIView):
    parser_classes = (CSVParser,)

    def post(self, request):
        # Save the highest institution id
        try:
            max_inst = Institution.objects.latest('id').id
        except ObjectDoesNotExist:
            max_inst = 0

        submitted_reports = []
        accepted_reports = []
        response_contains_valid = False

        csv_object = io.StringIO(request.data, newline=None)
        csv_handler = CSVHandler(csvfile=csv_object)
        csv_handler.handle()

        # Tracking
        client_ip, is_routable = get_client_ip(request)
        tracker = SubmissionTracker(original_data=request.data,
                                    origin='csv',
                                    user_profile=request.user.deqarprofile,
                                    ip_address=client_ip)
        tracker.log_package()

        if csv_handler.error:
            pass

        for data in csv_handler.submission_data:
            serializer = SubmissionPackageSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                populator = Populator(data=serializer.validated_data)
                populator.populate()
                flagger = ReportFlagger(report=populator.report)
                flagger.check_and_set_flags()
                tracker.log_report(populator, flagger)
                submitted_reports.append(self.make_success_response(populator, flagger))
                accepted_reports.append(self.make_success_response(populator, flagger))
                response_contains_valid = True
            else:
                submitted_reports.append(self.make_error_response(serializer, original_data={}))

        if response_contains_valid:
            send_submission_email.delay(response=accepted_reports,
                                        institution_id_max=max_inst,
                                        total_submission=len(submitted_reports),
                                        agency_email=request.user.email)
        return Response(submitted_reports, status=status.HTTP_200_OK)

    def make_success_response(self, populator, flagger):
        institution_warnings = populator.institution_flag_log
        report_warnings = flagger.flag_log

        if len(institution_warnings) > 0 or len(report_warnings) > 0:
            sanity_check_status = "warnings"
        else:
            sanity_check_status = "success"

        serializer = ReportResponseSerializer(flagger.report)

        return {
            'agency': populator.report.agency.deqar_id,
            'report': populator.report.id,
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
