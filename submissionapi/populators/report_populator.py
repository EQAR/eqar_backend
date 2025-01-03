import hashlib
import os
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from submissionapi.tasks import download_file

from reports.models import Report


class ReportPopulator():
    """
    Class to handle the population of report records from the submission endpoints.
    """
    def __init__(self, submission, agency, user):
        self.submission = submission
        self.agency = agency
        self.user = user
        self.report = None

    def populate(self):
        self.get_report_if_exists()
        self._report_upsert()
        self._report_file_upsert()

    def create(self):
        self._report_create()
        self._report_link_create()
        self._report_file_create()

    def update(self):
        self.get_report_if_exists()
        self._report_update()
        self._report_link_update()
        self._report_file_update()

    def get_report_if_exists(self):
        """
        Checks if there is a record existing with the submitted report_id or local identifier.
        """
        report = self.submission.get('report_id', None)
        if report:
            self.report = report
            return

        local_identifier = self.submission.get('local_identifier', None)
        if local_identifier is not None:
            try:
                self.report = Report.objects.get(agency=self.agency, local_identifier=local_identifier)
            except ObjectDoesNotExist:
                self.report = None

    def _report_create(self):
        activity = self.submission.get('esg_activity', None)
        report_name = activity.activity + ' (by ' + self.agency.acronym_primary + ')'

        self.report = Report(
            name=report_name,
            agency=self.agency,
            local_identifier=self.submission.get('local_identifier', None),
            status=self.submission.get('status', None),
            decision=self.submission.get('decision', None),
            valid_from=self.submission.get('valid_from', None),
            valid_to=self.submission.get('valid_to', None),
            created_by=self.user,
            other_comment=self.submission.get('other_comment', None),
            summary=self.submission.get('summary', None)
        )
        self.report.save()

        self._assign_agency_esg_activity_to_activities()
        self._assign_contributing_agencies()

    def _report_update(self):
        activity = self.submission.get('esg_activity', None)

        self.report.name = activity.activity + ' (by ' + self.agency.acronym_primary + ')'
        self.report.agency = self.agency
        self.report.local_identifier = self.submission.get('local_identifier', None)
        self.report.agency_esg_activity = activity
        self.report.agency_esg_activities.add(activity)
        self.report.status = self.submission.get('status', None)
        self.report.decision = self.submission.get('decision', None)
        self.report.valid_from = self.submission.get('valid_from', None)
        self.report.valid_to = self.submission.get('valid_to', None)
        self.report.updated_by = self.user
        self.report.updated_at = datetime.now()
        self.report.other_comment = self.submission.get('other_comment', None)
        self.report.summary = self.submission.get('summary', None)
        self.report.save()

        self._assign_agency_esg_activity_to_activities()
        self._assign_contributing_agencies()

    def _assign_contributing_agencies(self):
        contributing_agencies = self.submission.get('contributing_agencies', [])
        for contributing_agency in contributing_agencies:
            self.report.contributing_agencies.add(contributing_agency)

    def _assign_agency_esg_activity_to_activities(self):
        activity = self.submission.get('age', None)
        if activity:
            self.report.agency_esg_activities.add(activity)

    def _assign_agency_esg_activities(self):
        agency_esg_activities = self.submission.get('agency_esg_activities', [])
        for esg_activity in agency_esg_activities:
            self.report.agency_esg_activities.add(esg_activity)

    def _report_upsert(self):
        """
        Create or update a Report record.
        """
        # Update report
        if self.report is not None:
            self._report_update()
            self._report_link_update()
        # Create report
        else:
            self._report_create()
            self._report_link_create()

    def _report_link_create(self):
        """
            Create a ReportLink object.
        """
        report_links = self.submission.get('report_links', [])
        for report_link in report_links:
            self.report.reportlink_set.create(
                link_display_name=report_link.get('link_display_name', "View report record on agency site"),
                link=report_link.get('link', None)
            )

    def _report_link_update(self):
        """
        Update a ReportLink object.
        """
        report_links = self.submission.get('report_links', [])
        report_links_to_keep = [rl.get('link', None) for rl in report_links]

        # Remove existing report links
        self.report.reportlink_set.exclude(link__in=report_links_to_keep).delete()

        for report_link in report_links:
            link = report_link.get('link', None)
            if link is not None:
                rl, created = self.report.reportlink_set.get_or_create(
                    link=link
                )
                rl.link_display_name = report_link.get('link_display_name', "View report record on agency site")
                rl.save()

    def _report_file_create(self):
        """
        Create ReportFile instances.
        """
        report_files = self.submission.get('report_files', [])
        for report_file in report_files:
            languages = report_file.get('report_language', [])

            # If original_location is submitted
            original_location = report_file.get('original_location', "")
            file_display_name = report_file.get('display_name', None)
            if original_location != "":
                self._create_report_file_from_original_location(original_location, file_display_name, languages)

            # If file object was submitted as base64, save it to the disk and also generate checksum
            file = report_file.get('file', None)
            file_name = report_file.get('file_name', None)
            if file:
                self._create_report_file_from_base64_object(file, file_name, languages)

    def _report_file_update(self):
        pass

    def _create_report_file_from_original_location(self, original_location, file_display_name, languages):
        if file_display_name is None:
            url = original_location
            file_display_name = url[url.rfind("/") + 1:]

        rf = self.report.reportfile_set.create(
            file_display_name=file_display_name,
            file_original_location=original_location
        )

        # Async file download with celery
        download_file.delay(original_location, rf.id, self.agency.acronym_primary)

        for lang in languages:
            rf.languages.add(lang)

    def _create_report_file_from_base64_object(self, file, file_name, languages):
        rf = self.report.reportfile_set.create(
            file_display_name=file_name
        )
        agency_acronym = self.report.agency.acronym_primary
        file_path = os.path.join(settings.MEDIA_ROOT, agency_acronym,
                                 "%06d_%s_%s" % (rf.id, datetime.now().strftime("%Y%m%d_%H%M"), file_name))
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        with open(file_path, 'rb') as f:
            checksum = hashlib.md5(f.read()).hexdigest()
        rf.file = file_path
        rf.checksum = checksum,
        rf.save()

        for lang in languages:
            rf.languages.add(lang)

    def _report_file_upsert(self):
        """
        Create or update a ReportFile instance.
        """
        report_files = self.submission.get('report_files', None)
        if report_files is not None or report_files != '' or report_files != []:
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
                if original_location != "":
                    download_file.delay(original_location, rf.id, self.agency.acronym_primary)

                for lang in languages:
                    rf.languages.add(lang)
