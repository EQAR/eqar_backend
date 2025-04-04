from django.core.management import call_command, CommandError
from django.test import TestCase
from io import StringIO


class ReportCommandsTest(TestCase):
    """
    Test module for the Report Management Commands.
    """
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type', 'degree_outcome',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'programme_demo_01', 'programme_demo_02', 'programme_demo_03',
        'programme_demo_04', 'programme_demo_05', 'programme_demo_06',
        'programme_demo_07', 'programme_demo_08', 'programme_demo_09',
        'programme_demo_10', 'programme_demo_11', 'programme_demo_12',
        'report_decision', 'report_status',
        'users', 'report_demo_01'
    ]

    def test_reharvest_agency_wrong_acronym(self):
        with self.assertRaisesRegex(CommandError, 'Agency "NONEXISTING" does not exist'):
            call_command('reharvest_reports', '--agency=NONEXISTING')

    def test_reharvest_agency(self):
        out = StringIO()
        call_command('reharvest_reports', '--agency=EKKA', stdout=out)
        self.assertEqual('\nMissing: 0\nMissing, but not URL: 0\nWrong type: 0\nReharvest forced: 0\n', out.getvalue())

    def test_reharvest_report_wrong_id(self):
        with self.assertRaisesRegex(CommandError, 'Report ID "9999" does not exist'):
            call_command('reharvest_reports', '--report=9999')

    def test_reharvest_report_without_report_id_or_agency(self):
        with self.assertRaisesRegex(CommandError, 'Specify Agency, Report ID or --all.'):
            call_command('reharvest_reports')
