from django.test import TestCase
from django.conf import settings

from adminapi.serializers.report_serializers import ReportWriteSerializer
from reports.models import Report


class ReportWriteSerializerTest(TestCase):
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
        self.report = Report.objects.get(id=1)

    def test_valid_when_valid_to_exceeds_registration_valid_to_for_open_activity(self):
        serializer = ReportWriteSerializer(
            instance=self.report,
            data={
                'activities': [1],
                'institutions': [1],
                'status': 1,
                'valid_from': '2010-05-05',
                'valid_to': '2022-01-01',
            },
            partial=True
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_when_valid_from_exceeds_activity_valid_to(self):
        serializer = ReportWriteSerializer(
            instance=self.report,
            data={
                'activities': [5],
                'institutions': [1],
                'status': 1,
                'valid_from': '2014-01-01',
            },
            partial=True
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(settings.NON_FIELD_ERRORS_KEY, serializer.errors)
        self.assertIn('activity #5', str(serializer.errors[settings.NON_FIELD_ERRORS_KEY]))
