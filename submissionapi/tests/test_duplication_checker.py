from rest_framework.test import APITestCase

from reports.models import Report
from submissionapi.duplication_checker.report_duplication_checker import ReportDuplicationChecker


class DuplicationCheckerTestCase(APITestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eter_demo', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type', 'assessment',
        'agency_historical_field', 'degree_outcome',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'report_status', 'report_decision', 'users', 'report_demo_01_duplication'
    ]

    def test_duplication_not_found_string(self):
        report = Report.objects.get(pk=1)
        report_duplication_checker = ReportDuplicationChecker(report)
        self.assertFalse(report_duplication_checker.check())

    def test_duplication_found_string(self):
        report = Report.objects.get(pk=9)
        report_duplication_checker = ReportDuplicationChecker(report)
        self.assertTrue(report_duplication_checker.check())