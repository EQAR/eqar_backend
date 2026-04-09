from django.test import TestCase

from adminapi.serializers.agency_serializers import AgencyAdminWriteSerializer
from agencies.models import Agency


class AgencyAdminWriteSerializerTest(TestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'flag',
        'agency_historical_field',
        'agency_activity_type', 'agency_focus', 'permission_type',
        'eqar_decision_type',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo'
    ]

    def setUp(self):
        self.agency = Agency.objects.get(id=5)
        self.activity = self.agency.agencyesgactivity_set.first()

    def test_invalid_when_registration_start_after_activity_valid_from(self):
        serializer = AgencyAdminWriteSerializer(
            instance=self.agency,
            data={
                'registration_start': '2011-01-01',
                'activities': [
                    {
                        'id': self.activity.id,
                        'activity_group': self.activity.activity_group_id,
                        'activity': self.activity.activity,
                        'activity_valid_from': str(self.activity.activity_valid_from),
                    }
                ]
            },
            partial=True
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('activities', serializer.errors)
        self.assertIn('activity_valid_from', serializer.errors['activities'][0])

    def test_invalid_when_activity_valid_from_before_registration_start(self):
        serializer = AgencyAdminWriteSerializer(
            instance=self.agency,
            data={
                'activities': [
                    {
                        'id': self.activity.id,
                        'activity_group': self.activity.activity_group_id,
                        'activity': self.activity.activity,
                        'activity_valid_from': '2008-01-01',
                    }
                ]
            },
            partial=True
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('activities', serializer.errors)
        self.assertIn('registration_start', serializer.errors['activities'][0])

    def test_invalid_when_registration_valid_to_before_activity_valid_from(self):
        serializer = AgencyAdminWriteSerializer(
            instance=self.agency,
            data={
                'registration_valid_to': '2009-12-31',
                'activities': [
                    {
                        'id': self.activity.id,
                        'activity_group': self.activity.activity_group_id,
                        'activity': self.activity.activity,
                        'activity_valid_from': str(self.activity.activity_valid_from),
                    }
                ]
            },
            partial=True
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('activities', serializer.errors)
        self.assertIn('activity_valid_from', serializer.errors['activities'][0])

    def test_valid_when_activity_valid_from_within_registration_window(self):
        serializer = AgencyAdminWriteSerializer(
            instance=self.agency,
            data={
                'registration_start': '2009-01-01',
                'registration_valid_to': '2011-01-01',
                'activities': [
                    {
                        'id': self.activity.id,
                        'activity_group': self.activity.activity_group_id,
                        'activity': self.activity.activity,
                        'activity_valid_from': str(self.activity.activity_valid_from),
                    }
                ]
            },
            partial=True
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
