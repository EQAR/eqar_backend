import hashlib
import os
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from submissionapi.populators.report_file_populator import ReportFilePopulator
from submissionapi.tasks import download_file

from reports.models import Report, ReportFile


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
        self.report = Report(
            name=self._get_report_name(),
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

        self._assign_agency_esg_activities()
        self._assign_agency_esg_activity_to_activities()
        self._assign_contributing_agencies()

    def _report_update(self):
        self.report.name = self._get_report_name()
        self.report.agency = self.agency
        self.report.local_identifier = self.submission.get('local_identifier', None)
        self.report.status = self.submission.get('status', None)
        self.report.decision = self.submission.get('decision', None)
        self.report.valid_from = self.submission.get('valid_from', None)
        self.report.valid_to = self.submission.get('valid_to', None)
        self.report.updated_by = self.user
        self.report.updated_at = datetime.now()
        self.report.other_comment = self.submission.get('other_comment', None)
        self.report.summary = self.submission.get('summary', None)
        self.report.save()

        self._assign_agency_esg_activities()
        self._assign_agency_esg_activity_to_activities()
        self._assign_contributing_agencies()

    def _get_report_name(self):
        activities = self.submission.get('activities', [])
        activities = self._harmonize_activities(activities)

        name = []
        for activity in activities:
            name.append(activity.activity)
        report_name = ', '.join(name) + ' (by ' + self.agency.acronym_primary + ')'
        return report_name

    def _assign_contributing_agencies(self):
        contributing_agencies = self.submission.get('contributing_agencies', [])
        for contributing_agency in contributing_agencies:
            self.report.contributing_agencies.add(contributing_agency)

    def _assign_agency_esg_activity_to_activities(self):
        activity = self.submission.get('agency_esg_activity', None)
        if activity:
            self.report.agency_esg_activities.add(activity)

    def _assign_agency_esg_activities(self):
        activities = self.submission.get('activities', [])
        activities = self._harmonize_activities(activities)

        for activity in activities:
            self.report.agency_esg_activities.add(activity)

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
            report_file_populator = ReportFilePopulator(
                report_file_data=report_file,
                report=self.report,
                user=self.user
            )
            report_file_populator.report_file_create()

    def _report_file_update(self):
        """
        Update ReportFile instances.
        """
        report_files = self.submission.get('report_files', [])
        report_files_to_keep_by_id = [rf.get('report_file_id', None) for rf in report_files]

        # Remove existing report files
        self.report.reportfile_set.exclude(
            report_id=self.report.id,
            pk__in=report_files_to_keep_by_id
        ).delete()

        report_files = self.submission.get('report_files', [])
        for report_file_data in report_files:
            if 'report_file_id' in report_file_data:
                report_file = ReportFile.objects.get(pk=report_file_data.get('report_file_id'))
                report_file_populator = ReportFilePopulator(
                    report_file_data=report_file_data,
                    report_file=report_file,
                    report=self.report,
                    user=self.user
                )
                report_file_populator.report_file_update()
            else:
                report_file_populator = ReportFilePopulator(
                    report_file_data=report_file_data,
                    report=self.report,
                    user=self.user
                )
                report_file_populator.report_file_create()

    def _report_file_upsert(self):
        """
        Create or update a ReportFile instance. Used by the V1 endpoint only.
        """
        report_files = self.submission.get('report_files', None)
        report_files_to_keep_by_original_location = [rf.get('original_location', None) for rf in report_files]

        # Remove existing report files without matching original_location
        self.report.reportfile_set.exclude(
            report_id=self.report.id,
            file_original_location__in=report_files_to_keep_by_original_location
        ).delete()

        if report_files is not None or report_files != '' or report_files != []:
            for report_file in report_files:
                languages = report_file.get('report_language', [])
                file_display_name = report_file.get('display_name', None)
                if file_display_name is None:
                    url = report_file.get('original_location', "")
                    file_display_name = url[url.rfind("/")+1:]

                original_location = report_file.get('original_location', "")

                try:
                    rf, created = self.report.reportfile_set.get_or_create(
                        report_id=self.report.id,
                        file_display_name=file_display_name,
                        file_original_location=original_location
                    )
                except MultipleObjectsReturned:
                    rf = ReportFile.objects.filter(
                        report_id=self.report.id,
                        file_display_name=file_display_name,
                        file_original_location=original_location
                    ).first()

                # Async file download with celery
                if original_location != "":
                    download_file.delay(original_location, rf.id, self.agency.acronym_primary)

                for lang in languages:
                    rf.languages.add(lang)

    def _harmonize_activities(self, activities):
        # Harmonize activities
        harmonized_activities = []
        for activity in activities:
            if type(activity) == list:
                for a in activity:
                    harmonized_activities.append(a)
            else:
                harmonized_activities.append(activity)
        return harmonized_activities
