from django.conf import settings
from django.test import TestCase

from agencies.models import Agency, AgencyESGActivity
from lists.models import Language
from reports.models import ReportStatus, ReportDecision, Report
from submissionapi.populators.report_populator import ReportPopulator


class ReportPopulatorTestCase(TestCase):
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

    def test_init(self):
        populator = ReportPopulator(
            submission={},
            agency=Agency.objects.get(pk=5)
        )
        settings.TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
        self.assertEqual(populator.agency.acronym_primary, "ACQUIN")

    def test_get_report_if_exists_valid_identifier(self):
        populator = ReportPopulator(
            submission={},
            agency=Agency.objects.get(pk=5)
        )
        populator.submission = {'local_identifier': "EQARAG0021-EQARIN0001-01"}
        populator.get_report_if_exists()
        self.assertEqual(populator.report.id, 1)

    def test_get_report_if_exists_invalid_identifier(self):
        populator = ReportPopulator(
            submission={},
            agency=Agency.objects.get(pk=5)
        )
        populator.submission = {'local_identifier': "Random Non existent ID"}
        populator.get_report_if_exists()
        self.assertIsNone(populator.report)

    def test_report_upsert_existing_report(self):
        populator = ReportPopulator(
            submission={},
            agency=Agency.objects.get(pk=5)
        )
        esg_activity = AgencyESGActivity.objects.get(pk=1)
        status = ReportStatus.objects.get(pk=2)
        decision = ReportDecision.objects.get(pk=1)
        populator.submission = {
            'local_identifier': "EQARAG0021-EQARIN0001-01",
            'esg_activity': esg_activity,
            'status': status,
            'decision': decision,
            'valid_from': '2008-10-10'
        }
        populator.get_report_if_exists()
        populator._report_upsert()
        self.assertEqual(populator.report.status.id, 2)

    def test_repot_upsert_non_existing_report(self):
        populator = ReportPopulator(
            submission={},
            agency=Agency.objects.get(pk=5)
        )
        esg_activity = AgencyESGActivity.objects.get(pk=1)
        status = ReportStatus.objects.get(pk=2)
        decision = ReportDecision.objects.get(pk=1)
        populator.submission = {
            'local_identifier': "NonExistingReportID",
            'esg_activity': esg_activity,
            'status': status,
            'decision': decision,
            'valid_from': '2008-10-10'
        }
        populator.get_report_if_exists()
        populator._report_upsert()
        report = Report.objects.get(local_identifier='NonExistingReportID')
        self.assertEqual(report.status_id, 2)

    def test_report_link_upsert(self):
        populator = ReportPopulator(
            submission={},
            agency=Agency.objects.get(pk=5)
        )
        esg_activity = AgencyESGActivity.objects.get(pk=1)
        status = ReportStatus.objects.get(pk=2)
        decision = ReportDecision.objects.get(pk=1)
        populator.submission = {
            'local_identifier': "EQARAG0021-EQARIN0001-01",
            'esg_activity': esg_activity,
            'status': status,
            'decision': decision,
            'valid_from': '2008-10-10',
            'report_links': [
                {
                    "link": "http://example.com"
                }, {
                    "link": "http://example2.com",
                    "link_display_name": "Link display name example"
                }
            ]}
        populator.get_report_if_exists()
        populator._report_upsert()
        populator._report_link_upsert()
        self.assertEqual(populator.report.reportlink_set.count(), 2)
        self.assertEqual(populator.report.reportlink_set.first().link_display_name,
                         "View report record on agency site")

    def test_report_file_upsert(self):
        populator = ReportPopulator(
            submission={},
            agency=Agency.objects.get(pk=5)
        )
        esg_activity = AgencyESGActivity.objects.get(pk=1)
        status = ReportStatus.objects.get(pk=2)
        decision = ReportDecision.objects.get(pk=1)
        populator.submission = {
            'local_identifier': "EQARAG0021-EQARIN0001-01",
            'esg_activity': esg_activity,
            'status': status,
            'decision': decision,
            'valid_from': '2008-10-10',
            'report_files': [
                {
                    "original_location": "http://example.com/example.pdf",
                    "report_language": [Language.objects.get(pk=1)]
                }, {
                    "original_location": "http://example2.com/example2.pdf",
                    "display_name": "2nd example document",
                    "report_language": [Language.objects.get(pk=1), Language.objects.get(pk=2)]
                }
            ]}
        populator.get_report_if_exists()
        populator._report_upsert()
        populator._report_file_upsert()
        self.assertEqual(populator.report.reportfile_set.count(), 2)
        self.assertEqual(populator.report.reportfile_set.first().file_display_name,
                         "example.pdf")
        self.assertEqual(populator.report.reportfile_set.all()[0].file_display_name,
                         "2nd example document")
        self.assertEqual(populator.report.reportfile_set.first().languages.count(), 1)
        self.assertEqual(populator.report.reportfile_set.all()[0].languages.count(), 2)
