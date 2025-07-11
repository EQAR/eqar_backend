from ipware import get_client_ip

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction

from institutions.models import Institution
from reports.models import ReportUpdateLog
from submissionapi.flaggers.report_flagger import ReportFlagger
from submissionapi.populators.populator import Populator
from submissionapi.v2.serializers.response_serializers import ResponseReportSerializer
from submissionapi.trackers.submission_tracker import SubmissionTracker
from submissionapi.tasks import send_submission_email


class SubmissionPackageHandler:
    def __init__(self, request, serializer, action):
        self.max_inst = self._get_max_inst()
        self.request = request
        self.serializer = serializer
        self.action = action
        self.status = 'success'
        self.response = {}
        self.populator = None
        self.flagger = None

    def handle(self):
        # Tracking
        client_ip, is_routable = get_client_ip(self.request)
        tracker = SubmissionTracker(original_data=self.request.data,
                                    origin='api-v2',
                                    user_profile=self.request.user.deqarprofile,
                                    ip_address=client_ip)
        tracker.log_package()

        if self.serializer.is_valid():
            self.populator = Populator(data=self.serializer.validated_data, user=self.request.user)
            try:
                with transaction.atomic():
                    self.populator.populate(action=self.action)
            except ValidationError as error:
                if hasattr(error, "error_dict"):
                    tracker.log_errors(dict(error))
                else:
                    tracker.log_errors(list(error))
                raise
            self.flagger = ReportFlagger(report=self.populator.report)
            self.flagger.check_and_set_flags()
            # Add submission report log
            tracker.log_report(self.populator, self.flagger)
            # Add log entry
            ReportUpdateLog.objects.create(
                report=self.populator.report,
                note="Report %sd via API." % self.action,
                updated_by=self.request.user
            )
            self._make_success_response()
            # Send email
            send_submission_email.delay(response=[self.response],
                                        institution_id_max=self.max_inst,
                                        total_submission=1,
                                        agency_email=self.request.user.email)
        else:
            self.status = 'error'
            # Add error to package log
            tracker.log_errors(self.serializer.errors)
            self._make_error_response()

    def _get_max_inst(self):
        # Save the highest institution id
        try:
            max_inst = Institution.objects.latest('id').id
        except ObjectDoesNotExist:
            max_inst = 0
        return max_inst

    def _make_success_response(self):
        institution_warnings = self.populator.institution_flag_log
        report_warnings = [fl.flag_message for fl in self.flagger.report.reportflag_set.filter(active=True)]

        if len(institution_warnings) > 0 or len(report_warnings) > 0:
            sanity_check_status = "warnings"
        else:
            sanity_check_status = "success"

        serializer = ResponseReportSerializer(self.flagger.report)

        self.response = {
            'submission_status': 'success',
            'submitted_report': serializer.data,
            'sanity_check_status': sanity_check_status,
            'report_flag': self.flagger.report.flag.flag,
            'report_warnings': report_warnings,
            'institution_warnings': institution_warnings
        }

    def _make_error_response(self):
        self.response = {
            'submission_status': 'errors',
            'original_data': self.request.data,
            'errors': self.serializer.errors
        }
