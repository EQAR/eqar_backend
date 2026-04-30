import shutil
import tempfile
from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings

from reports.models import Report, ReportFile
from submissionapi.tasks import download_file


class CeleryTaskTestCase(TestCase):
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
        settings.CELERY_ALWAYS_EAGER = True
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        settings.ADMINS = [('Admin', 'admin@example.com')]

    def test_download_file(self):
        report = Report.objects.get(pk=1)
        result = download_file.apply(args=('https://education.github.com/git-cheat-sheet-education.pdf', 1, 'ACQUIN'))
        self.assertTrue(result.successful())
        rf = report.reportfile_set.first()
        saved_name = rf.file.name
        self.assertIn('git-cheat-sheet-education', saved_name, msg=f"Actual saved filename: {saved_name}")
        self.assertTrue(saved_name.endswith('.pdf'), msg=f"Actual saved filename: {saved_name}")
        self.assertEqual(rf.download_status, ReportFile.DOWNLOAD_STATUS_SUCCESS)

    def test_send_submission_email(self):
        pass

    def test_download_file_sends_email_on_failure(self):
        result = download_file.apply(args=('https://backend.deqar.eu/URL/FOR/SURE/DOES/NOT/EXIST', 1, 'ACQUIN'))
        self.assertFalse(result.successful())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("ReportDownloader failure for report_file 1", mail.outbox[0].subject)
        report = Report.objects.get(pk=1)
        rf = report.reportfile_set.first()
        self.assertEqual(rf.download_status, ReportFile.DOWNLOAD_STATUS_FAILED)
