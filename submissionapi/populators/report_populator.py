from django.core.exceptions import ObjectDoesNotExist
from submissionapi.tasks import download_file

from reports.models import Report


class ReportPopulator():
    """
    Class to handle the population of report records from the submission endpoints.
    """
    def __init__(self, submission, agency):
        self.submission = submission
        self.agency = agency
        self.report = None

    def populate(self):
        self.get_report_if_exists()
        self._report_upsert()
        self._report_link_upsert()
        self._report_file_upsert()

    def get_report_if_exists(self):
        """
        Checks if there is a record existing with the submitted local identifier.
        """
        local_identifier = self.submission.get('local_identifier', None)
        if local_identifier is not None:
            try:
                self.report = Report.objects.get(agency=self.agency, local_identifier=local_identifier)
            except ObjectDoesNotExist:
                self.report = None

    def _report_upsert(self):
        """
        Create or update a Report record.
        """
        activity = self.submission.get('esg_activity', None)
        report_name = activity.activity + ' (by ' + self.agency.acronym_primary + ')'

        # Update report
        if self.report is not None:
            self.report.name = report_name
            self.report.agency = self.agency
            self.report.local_identifier = self.submission.get('local_identifier', None)
            self.report.agency_esg_activity = activity
            self.report.status = self.submission.get('status', None)
            self.report.decision = self.submission.get('decision', None)
            self.report.valid_from = self.submission.get('valid_from', None)

        # Create report
        else:
            self.report = Report(
                name=report_name,
                agency=self.agency,
                local_identifier=self.submission.get('local_identifier', None),
                agency_esg_activity=self.submission.get('esg_activity', None),
                status=self.submission.get('status', None),
                decision=self.submission.get('decision', None),
                valid_from=self.submission.get('valid_from', None),
                valid_to=self.submission.get('valid_to', None),
            )
        self.report.save()

    def _report_link_upsert(self):
        """
        Create or update a ReportLink object.
        """
        report_links = self.submission.get('report_links', None)
        if report_links is not None:
            # Remove existing report links
            self.report.reportlink_set.all().delete()
            for report_link in report_links:
                self.report.reportlink_set.create(
                    link_display_name=report_link.get('link_display_name', "View report record on agency site"),
                    link=report_link.get('link', None)
                )

    def _report_file_upsert(self):
        """
        Create or update a ReportFile instance.
        """
        report_files = self.submission.get('report_files', None)
        if report_files is not None:
            # Remove existing report files
            self.report.reportfile_set.all().delete()
            for report_file in report_files:
                languages = report_file.get('report_language', [])
                file_display_name = report_file.get('display_name', None)
                if file_display_name is None:
                    url = report_file.get('original_location', "")
                    file_display_name = url[url.rfind("/")+1:]

                original_location = report_file.get('original_location', "")
                rf = self.report.reportfile_set.create(
                    file_display_name=file_display_name,
                    file_original_location=original_location
                )

                # Async file download with celery
                download_file.delay(original_location, rf.id, self.agency.acronym_primary)

                for lang in languages:
                    rf.languages.add(lang)
