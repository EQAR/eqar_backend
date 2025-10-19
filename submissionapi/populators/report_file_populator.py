import hashlib
import os
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from submissionapi.tasks import download_file
from django.conf import settings


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
            file_original_location=original_location
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
        self.report_file.save()

        # Async file download with celery
        download_file.delay(original_location, self.report_file.id, self.agency.acronym_primary)

        self.report_file.languages.clear()
        for lang in languages:
            self.report_file.languages.add(lang)


    def _create_report_file_from_base64_object(self, file, file_name, languages):
        rf = self.report.reportfile_set.create(
            file_display_name=file_name
        )
        agency_acronym = self.agency.acronym_primary
        file_base_path = os.path.join(agency_acronym,
                                 "%06d_%s_%s" % (rf.id, datetime.now().strftime("%Y%m%d_%H%M"), file_name))
        file_path = os.path.join(settings.MEDIA_ROOT, file_base_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        with open(file_path, 'rb') as f:
            checksum = hashlib.md5(f.read()).hexdigest()
        rf.file = file_base_path
        rf.checksum = checksum,
        rf.save()

        for lang in languages:
            rf.languages.add(lang)

    def _update_report_file_from_base64_object(self, file, file_name, languages):
        agency_acronym = self.agency.acronym_primary
        file_base_path = os.path.join(agency_acronym,
                                 "%06d_%s_%s" % (self.report_file.id, datetime.now().strftime("%Y%m%d_%H%M"), file_name))
        file_path = os.path.join(settings.MEDIA_ROOT, file_base_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        with open(file_path, 'rb') as f:
            checksum = hashlib.md5(f.read()).hexdigest()
        self.report_file.file = file_base_path
        self.report_file.checksum = checksum
        self.report_file.save()

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