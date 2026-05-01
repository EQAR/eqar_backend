import shutil
import tempfile

from django.test import TestCase
from django.test.utils import override_settings

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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._temp_media_root = tempfile.mkdtemp(prefix='test_media_')
        cls._media_override = override_settings(MEDIA_ROOT=cls._temp_media_root)
        cls._media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._media_override.disable()
        shutil.rmtree(cls._temp_media_root, ignore_errors=True)
        super().tearDownClass()

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
        self.assertFalse(downloader.report_file.file)

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
        saved_name = downloader.report_file.file.name
        self.assertIn(
            "northern-university-expert-report-2",
            saved_name,
            msg=f"Actual saved filename: {saved_name}",
        )
        self.assertTrue(saved_name.endswith(".pdf"), msg=f"Actual saved filename: {saved_name}")

    def test_get_filename_from_cd_parsing(self):
        # No header → None
        self.assertIsNone(ReportDownloader._get_filename_from_cd(None))
        self.assertIsNone(ReportDownloader._get_filename_from_cd(''))

        # Plain ASCII filename
        self.assertEqual(
            ReportDownloader._get_filename_from_cd('attachment; filename="report.pdf"'),
            'report.pdf',
        )

        # RFC 5987 extended form with UTF-8 percent-encoded characters
        # (the regression that prompted the fix: previously this returned None
        # because get_param('filename') ignored the extended form)
        self.assertEqual(
            ReportDownloader._get_filename_from_cd(
                "attachment; filename*=UTF-8''na%C3%AFve%20r%C3%A9port.pdf"
            ),
            'naïve réport.pdf',
        )

    def test_download_file(self):
        downloader = ReportDownloader(
            url="http://www.musique-qe.eu/userfiles/File/2008-06-report-groningen-website.pdf",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertIsNone(downloader.old_file_path)
        downloader.download()
        self.assertTrue(downloader.report_file.file)
        saved_name = downloader.report_file.file.name
        self.assertIn(
            "2008-06-report-groningen-website",
            saved_name,
            msg=f"Actual saved filename: {saved_name}",
        )
        self.assertTrue(saved_name.endswith(".pdf"), msg=f"Actual saved filename: {saved_name}")
        downloader2 = ReportDownloader(
            url="http://www.musique-qe.eu/userfiles/File/2008-06-report-groningen-website.pdf",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        old_name = downloader2.old_file_path
        self.assertIn(
            "2008-06-report-groningen-website",
            old_name,
            msg=f"Actual previously saved filename: {old_name}",
        )
        self.assertTrue(old_name.endswith(".pdf"), msg=f"Actual previously saved filename: {old_name}")
