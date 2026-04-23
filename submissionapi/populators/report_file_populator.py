from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile

from reports.models import ReportFile
from submissionapi.tasks import download_file


class ReportFilePopulator():
    """
    Class to handle the population of report records from the submission endpoints.
    """
    def __init__(self, user, report, report_file_data=None, report_file=None):
        self.report = report
        self.agency = report.agency
        self.user = user
        self.report_file = report_file
        self.report_file_data = report_file_data

    def report_file_create(self):
        """
        Create ReportFile instance.
        """
        languages = self.report_file_data.get('report_language', [])

        # If original_location is submitted
        original_location = self.report_file_data.get('original_location', "")
        file_display_name = self.report_file_data.get('display_name', None)
        if original_location != "":
            self._create_report_file_from_original_location(original_location, file_display_name, languages)

        # If file object was submitted as base64, save it to the disk and also generate checksum
        file = self.report_file_data.get('file', None)
        file_name = self.report_file_data.get('file_name', None)
        if file:
            self._create_report_file_from_base64_object(file, file_name, languages)

    def report_file_update(self):
        """
        Update ReportFile instance.
        """
        try:
            languages = self.report_file_data.get('report_language', [])

            # If original_location is submitted
            original_location = self.report_file_data.get('original_location', "")
            file_display_name = self.report_file_data.get('display_name', None)
            if original_location != "":
                self._update_report_file_from_original_location(original_location, file_display_name, languages)

            # If file object was submitted as base64, save it to the disk and also generate checksum
            file = self.report_file_data.get('file', None)
            file_name = self.report_file_data.get('file_name', None)
            if file:
                self._update_report_file_from_base64_object(file, file_name, languages)

        except ObjectDoesNotExist:
            pass

    def _create_report_file_from_original_location(self, original_location, file_display_name, languages):
        if file_display_name is None:
            url = original_location
            file_display_name = url[url.rfind("/") + 1:]

        rf = self.report.reportfile_set.create(
            file_display_name=file_display_name,
            file_original_location=original_location,
            download_status=ReportFile.DOWNLOAD_STATUS_PENDING
        )

        # Async file download with celery
        download_file.delay(original_location, rf.id, self.agency.acronym_primary)

        for lang in languages:
            rf.languages.add(lang)

    def _update_report_file_from_original_location(self, original_location, file_display_name, languages):
        if file_display_name is None:
            url = original_location
            file_display_name = url[url.rfind("/") + 1:]

        self.report_file.file_display_name = file_display_name
        self.report_file.file_original_location = original_location
        self.report_file.download_status = ReportFile.DOWNLOAD_STATUS_PENDING
        self.report_file.save()

        # Async file download with celery
        download_file.delay(original_location, self.report_file.id, self.agency.acronym_primary)

        self.report_file.languages.clear()
        for lang in languages:
            self.report_file.languages.add(lang)


    def _create_report_file_from_base64_object(self, file, file_name, languages):
        rf = self.report.reportfile_set.create(file_display_name=file_name)
        content = ContentFile(b''.join(file.chunks()))
        rf.file.save(file_name, content, save=True)
        for lang in languages:
            rf.languages.add(lang)

    def _update_report_file_from_base64_object(self, file, file_name, languages):
        self.report_file.file.delete(save=False)
        content = ContentFile(b''.join(file.chunks()))
        self.report_file.file.save(file_name, content, save=True)
        self.report_file.languages.clear()
        for lang in languages:
            self.report_file.languages.add(lang)

    def check_permission(self):
        """
        Check if the user has permission to create/update the report file.
        """
        submitting_agency = self.user.deqarprofile.submitting_agency
        if submitting_agency.agency_allowed(self.agency):
            return True
        else:
            return False
