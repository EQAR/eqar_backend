from django.test import TestCase
from reports.models import Report


class ReportTestCase(TestCase):
    """
    Test module for the Report classes.
    """
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eter_demo', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'programme_demo_01', 'programme_demo_02', 'programme_demo_03',
        'programme_demo_04', 'programme_demo_05', 'programme_demo_06',
        'programme_demo_07', 'programme_demo_08', 'programme_demo_09',
        'programme_demo_10', 'programme_demo_11', 'programme_demo_12',
        'report_decision', 'report_status',
        'report_demo_01'
    ]

    def test_report_status_str(self):
        report_status = Report.objects.get(id=1).status
        self.assertEqual(str(report_status), 'part of obligatory EQA system')

    def test_report_decision_str(self):
        report_status = Report.objects.get(id=1).decision
        self.assertEqual(str(report_status), 'positive')
