from django.core.exceptions import ObjectDoesNotExist
from institutions.models import Institution
from reports.models import ReportUpdateLog
from submissionapi.flaggers.report_flagger import ReportFlagger
from submissionapi.populators.populator import Populator
from submissionapi.v2.serializers.response_serializers import ResponseReportSerializer
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
        if self.serializer.is_valid():
            self.populator = Populator(data=self.serializer.validated_data, user=self.request.user)
            self.populator.populate(action=self.action)
            self.flagger = ReportFlagger(report=self.populator.report)
            self.flagger.check_and_set_flags()
            send_submission_email.delay(response=[self._make_success_response()],
                                        institution_id_max=self.max_inst,
                                        total_submission=1,
                                        agency_email=self.request.user.email)
            # Add log entry
            ReportUpdateLog.objects.create(
                report=self.populator.report,
                note="Report %sd via API." % self.action,
                updated_by=self.request.user
            )
            self._make_success_response()
        else:
            self.status = 'error'
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