import os
from django.test import TestCase

from requests.exceptions import HTTPError
from lists.models import Language
from reports.models import ReportFile, Report
from submissionapi.downloaders.report_downloader import ReportDownloader, WrongFileType, FileTooLarge


class ReportDownloaderTestCase(TestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type', 'degree_outcome',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'programme_demo_01', 'programme_demo_02', 'programme_demo_03',
        'programme_demo_04', 'programme_demo_05', 'programme_demo_06',
        'programme_demo_07', 'programme_demo_08', 'programme_demo_09',
        'programme_demo_10', 'programme_demo_11', 'programme_demo_12',
        'report_decision', 'report_status',
        'users', 'report_demo_01'
    ]

    def setUp(self):
        self.report_file = ReportFile.objects.create(
            report=Report.objects.get(id=1),
            file_display_name='Test File',
            file_original_location='http://www.example.com/example.pdf',
        )
        self.report_file.languages.add(Language.objects.get(iso_639_1='fr'))

    def test_init(self):
        downloader = ReportDownloader(
            url=self.report_file.file_original_location,
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertEqual(downloader.agency_acronym, "SPACE")
        self.assertEqual(downloader.url, "http://www.example.com/example.pdf")

    def test_is_downloadable_false(self):
        downloader = ReportDownloader(
            url="https://backend.deqar.eu/URL/FOR/SURE/DOES/NOT/EXIST",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertRaises(HTTPError, downloader.download)

    def test_wrong_content_type(self):
        downloader = ReportDownloader(
            url="https://www.youtube.com/watch?v=mwtjWym2wOs",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertRaises(WrongFileType, downloader.download)
        self.assertFalse(os.path.isfile(downloader.saved_file_path))

    def test_file_too_large(self):
        downloader = ReportDownloader(
            url="https://raw.githubusercontent.com/TestFileHub/FileHub/main/pdf/pdf100mb.pdf",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertRaises(FileTooLarge, downloader.download)

    def test_get_filename_from_content_disposition(self):
        downloader = ReportDownloader(
            url="http://www.anqa.am/en/accreditation/expert-reports/"
                "expert-panel-report-on-institutional-re-accreditation-carried-out-at-northern-university/",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        downloader.download()
        self.assertTrue("northern-university-expert-report-2.pdf" in downloader.saved_file_path)
        os.remove(downloader.saved_file_path)

    def test_download_file(self):
        downloader = ReportDownloader(
            url="http://www.musique-qe.eu/userfiles/File/2008-06-report-groningen-website.pdf",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertIsNone(downloader.old_file_path)
        downloader.download()
        self.assertTrue(os.path.exists(downloader.saved_file_path))
        self.assertTrue("2008-06-report-groningen-website.pdf" in downloader.saved_file_path)
        downloader2 = ReportDownloader(
            url="http://www.musique-qe.eu/userfiles/File/2008-06-report-groningen-website.pdf",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertTrue("2008-06-report-groningen-website.pdf" in downloader2.old_file_path)
        os.remove(downloader.saved_file_path)

