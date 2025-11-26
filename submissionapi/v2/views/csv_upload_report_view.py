import io
import traceback
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from ipware import get_client_ip
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from institutions.models import Institution
from reports.models import ReportUpdateLog
from submissionapi.csv_functions.csv_handler import CSVHandler
from submissionapi.csv_functions.csv_parser import CSVParser
from submissionapi.flaggers.report_flagger import ReportFlagger
from submissionapi.populators.populator import Populator
from submissionapi.v2.serializers.response_serializers import ResponseCSVReportSerializer
from submissionapi.v2.serializers.submisson_serializers import SubmissionPackageSerializer
from submissionapi.tasks import send_submission_email
from submissionapi.trackers.submission_tracker import SubmissionTracker


class SubmissionCSVView(APIView):
    parser_classes = (CSVParser,)
    swagger_schema = None

    def post(self, request):
        # Get highest institution ID before import starts
        try:
            max_inst = Institution.objects.latest('id').id
        except ObjectDoesNotExist:
            max_inst = 0

        submitted_reports = []
        accepted_reports = []
        error_messages = []
        response_contains_valid = False

        # Read CSV into handler
        csv_object = io.StringIO(request.data, newline=None)
        csv_handler = CSVHandler(csvfile=csv_object)
        csv_handler.handle()

        # Track request
        client_ip, _ = get_client_ip(request)
        tracker = SubmissionTracker(
            original_data=request.data,
            origin='csv',
            user_profile=request.user.deqarprofile,
            ip_address=client_ip
        )
        tracker.log_package()

        # If parsing failed before any row was processed
        if csv_handler.error:
            # You may want to return a 400 here
            pass

        # ----------------------------
        # Process rows one by one
        # ----------------------------
        for data in csv_handler.submission_data:

            # Each row gets its own savepoint
            with transaction.atomic():
                try:
                    serializer = SubmissionPackageSerializer(
                        data=data,
                        context={'request': request}
                    )

                    if not serializer.is_valid():
                        # No DB writes yet → nothing to roll back
                        report_id = data.get('report_id')
                        error_messages.append(serializer.errors)
                        submitted_reports.append(
                            self.make_error_response(serializer, {}, report_id)
                        )
                        continue

                    # Populate (this may write to DB)
                    populator = Populator(
                        data=serializer.validated_data,
                        user=request.user
                    )

                    try:
                        populator.populate()
                    except ValidationError as ve:
                        # Expected validation issue → rollback row
                        if hasattr(ve, "error_dict"):
                            tracker.log_errors(dict(ve))
                            error_messages.append(dict(ve))
                        else:
                            tracker.log_errors(list(ve))
                            error_messages.append(list(ve))

                        submitted_reports.append(
                            self.make_error_response(serializer, {}, data.get('report_id'))
                        )
                        continue

                    # Flag & log
                    flagger = ReportFlagger(report=populator.report)
                    flagger.check_and_set_flags()
                    tracker.log_report(populator, flagger)

                    # Row success output
                    success = self.make_success_response(populator, flagger)
                    submitted_reports.append(success)
                    accepted_reports.append(success)
                    error_messages.append(None)
                    response_contains_valid = True

                    # Add update log
                    ReportUpdateLog.objects.create(
                        report=populator.report,
                        note="Report updated via CSV.",
                        updated_by=request.user
                    )

                except Exception as unexpected:
                    # ----------------------------
                    # Catch ANY unexpected errors
                    # Roll back row only
                    # ----------------------------
                    trace = traceback.format_exc()
                    error_payload = {
                        "unexpected_error": str(unexpected),
                        "traceback": trace
                    }
                    error_messages.append(error_payload)
                    tracker.log_errors(error_payload)

                    submitted_reports.append({
                        'report': data.get('report_id'),
                        'submission_status': 'errors',
                        'original_data': data,
                        'errors': [[f"Server error! - {str(unexpected)}"]]
                    })

                    # Continue to next row safely
                    continue

        # Final track of all errors
        tracker.log_errors(error_messages)

        # Only send success email if at least one row was valid
        if response_contains_valid:
            send_submission_email.delay(
                response=accepted_reports,
                institution_id_max=max_inst,
                total_submission=len(submitted_reports),
                agency_email=request.user.email
            )

        return Response(submitted_reports, status=status.HTTP_200_OK)

    # ------------------------------------
    # Helpers (untouched)
    # ------------------------------------
    def make_success_response(self, populator, flagger):
        institution_warnings = populator.institution_flag_log
        report_warnings = [
            fl.flag_message for fl in flagger.report.reportflag_set.filter(active=True)
        ]

        sanity_check_status = (
            "warnings" if institution_warnings or report_warnings else "success"
        )

        serializer = ResponseCSVReportSerializer(flagger.report)

        return {
            'agency': populator.report.agency.deqar_id,
            'report': populator.report.id,
            'submission_status': 'success',
            'submitted_report': serializer.data,
            'sanity_check_status': sanity_check_status,
            'report_flag': flagger.report.flag.flag,
            'report_warnings': report_warnings,
            'institution_warnings': institution_warnings,
        }

    def make_error_response(self, serializer, original_data, report_id):
        return {
            'report': report_id,
            'submission_status': 'errors',
            'original_data': original_data,
            'errors': serializer.errors
        }
