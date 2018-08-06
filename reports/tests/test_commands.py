from django.core.management import call_command, CommandError
from django.test import TestCase
from django.utils.six import StringIO


class ReportCommandsTest(TestCase):
    """
    Test module for the Report Management Commands.
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

    def test_reharvest_agency_wrong_acronym(self):
        with self.assertRaisesRegex(CommandError, 'Agency "NONEXISTING" does not exist'):
            call_command('reharvest_agency', '--agency=NONEXISTING')

    def test_reharvest_agency_without_agency(self):
        with self.assertRaisesRegex(CommandError, '--agency parameter should be set.'):
            call_command('reharvest_agency')

    def test_reharvest_agency(self):
        out = StringIO()
        call_command('reharvest_agency', '--agency=EKKA', stdout=out)
        self.assertEqual('', out.getvalue())

    def test_reharvest_report_wrong_id(self):
        with self.assertRaisesRegex(CommandError, 'Report ID "9999" does not exist'):
            call_command('reharvest_report', '--report=9999')

    def test_reharvest_report_without_id(self):
        with self.assertRaisesRegex(CommandError, '--report parameter should be set.'):
            call_command('reharvest_report')

    def test_reharvest_report(self):
        out = StringIO()
        call_command('reharvest_report', '--report=1', stdout=out)
        self.assertEqual('', out.getvalue())