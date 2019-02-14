import os
from django.test import TestCase

from lists.models import Language
from reports.models import ReportFile, Report
from submissionapi.downloaders.report_downloader import ReportDownloader


class ReportDownloaderTestCase(TestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eter_demo', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type',
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
        'report_demo_01'
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

    def test_is_downloadable_true(self):
        downloader = ReportDownloader(
            url="http://www.musique-qe.eu/userfiles/File/2008-06-report-groningen-website.pdf",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertEqual(downloader._url_is_downloadable(), True)

    def test_is_downloadable_false(self):
        downloader = ReportDownloader(
            url="https://www.youtube.com/watch?v=mwtjWym2wOs",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertEqual(downloader._url_is_downloadable(), False)

    def test_get_filename_from_url(self):
        downloader = ReportDownloader(
            url="http://www.musique-qe.eu/userfiles/File/2008-06-report-groningen-website.pdf",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertTrue("2008-06-report-groningen-website.pdf" in downloader._get_filename())

    def test_get_filename_from_content_disposition(self):
        downloader = ReportDownloader(
            url="http://www.anqa.am/en/accreditation/expert-reports/"
                "expert-panel-report-on-institutional-re-accreditation-carried-out-at-northern-university/",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertTrue("northern-university-expert-report-2.pdf" in downloader._get_filename())

    def test_get_filename_url_encoded(self):
        downloader = ReportDownloader(
            url="https://iqaa.kz/images/otchety/Specialized_Accreditation/2018/rus/"
                "6D070200%20%E2%80%93%20%C2%AB%D0%90%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D1%82%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%"
                "D1%8F%20%20%D0%B8%20%D1%83%D0%BF%D1%80%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5_%D0%9A%D0%A3%D0%9F%D0"
                "%A1_%D0%BE%D1%82%D1%87%D0%B5%D1%82%D1%8B_2018%D1%80%D1%83%D1%81.pdf",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        self.assertTrue("Автоматизация" in downloader._get_filename())

    def test_download_file(self):
        downloader = ReportDownloader(
            url="http://www.musique-qe.eu/userfiles/File/2008-06-report-groningen-website.pdf",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        downloader.download()
        self.assertTrue(os.path.exists(downloader.saved_file_path))
        os.remove(downloader.saved_file_path)

    def test_get_old_file_path_not_exists(self):
        downloader = ReportDownloader(
            url="http://www.musique-qe.eu/userfiles/File/2008-06-report-groningen-website.pdf",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        downloader._get_old_file_path()
        self.assertEqual(downloader.old_file_path, "")

    def test_get_old_file_path_exists(self):
        downloader = ReportDownloader(
            url="http://www.musique-qe.eu/userfiles/File/2008-06-report-groningen-website.pdf",
            report_file_id=self.report_file.id,
            agency_acronym='SPACE'
        )
        downloader.download()
        downloader._get_old_file_path()
        self.assertTrue("2008-06-report-groningen-website.pdf" in downloader.old_file_path)
