import datetime
import json

from submissionapi.models import SubmissionPackageLog, SubmissionReportLog
from submissionapi.populators.populator import Populator


class SubmissionTracker:
    def __init__(self, original_data, origin, user_profile, ip_address):
        self.original_data = original_data
        self.origin = origin
        self.submisson_date = datetime.date.today()
        self.submission_report_logs = []
        self.user_profile = user_profile
        self.ip_address = ip_address
        self.spl = None

    def log_package(self):
        self.spl = SubmissionPackageLog.objects.create(
            user=self.user_profile,
            user_ip_address=self.ip_address,
            origin=self.origin,
            submitted_data=self.original_data,
        )

    def log_report(self, populator, flagger):
        # populator can be instance of submissionapi.populators.populator.Populator of reports.models.Report
        SubmissionReportLog.objects.create(
            submission_package_log=self.spl,
            agency=populator.agency,
            report=flagger.report,
            report_status=flagger.report.flag,
            report_warnings=json.dumps([fl.flag_message for fl in flagger.report.reportflag_set.all()]),
            institution_warnings=json.dumps(populator.institution_flag_log if isinstance(populator, Populator) else [])
        )

    def log_errors(self, errors):
        self.spl.submission_errors = json.dumps(errors)
        self.spl.save()

