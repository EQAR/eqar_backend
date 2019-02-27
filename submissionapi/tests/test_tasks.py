import os
from django.conf import settings
from django.test import TestCase

from reports.models import Report
from submissionapi.tasks import download_file


class CeleryTaskTestCase(TestCase):
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
        'users', 'report_demo_01'
    ]

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

    def test_download_file(self):
        report = Report.objects.get(pk=1)
        result = download_file.apply(args=('https://education.github.com/git-cheat-sheet-education.pdf', 1, 'ACQUIN'))
        self.assertTrue(result.successful())
        rf = report.reportfile_set.first()
        self.assertTrue('git-cheat-sheet-education.pdf' in rf.file.name)

    def test_send_submission_email(self):
        pass

    def tearDown(self):
        report = Report.objects.get(pk=1)
        rf = report.reportfile_set.first()
        if rf.file:
            rf.file.delete()