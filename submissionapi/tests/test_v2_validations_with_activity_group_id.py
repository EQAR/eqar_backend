from django.contrib.auth.models import User
from django.test import RequestFactory
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from accounts.models import DEQARProfile
from agencies.models import SubmittingAgency
from submissionapi.v2.serializers.submisson_serializers import SubmissionPackageCreateSerializer


class SubmissionV2ValidationTestCaseWithActivityGroup(APITestCase):
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
        self.valid_data = {
            "agency": "ACQUIN",
            "contributing_agencies": ["EKKA"],
            "valid_from": "2010-05-05",
            "date_format": "%Y-%M-%d",
            "activities": [
                {
                    "group": "5"
                }
            ],
            "status": "1",
            "decision": "1",
            "report_files": [
                {
                    "original_location": "http://backend.deqar.eu/reports/AAQ/100676_20210104_0959_2018-09-14-bericht-systemakkreditierung-rwth-aachen.pdf",
                    "report_language": ["eng"]
                }
            ],
            "institutions": [
                {
                    "eter_id": "DE0392",
                    "identifier": "DE0001",
                    "resource": "national identifier"
                }
            ],
            "programmes": [
                {
                    "name_primary": "Programme name",
                    "qf_ehea_level": "2",
                    "degree_outcome": "full degree",
                }
            ]
        }
        self.user = User.objects.create_superuser(username='testuer',
                                                  email='testuser@eqar.eu',
                                                  password='testpassword')
        self.user.save()

        submitting_agency = SubmittingAgency.objects.get(pk=1)
        self.deqar_profile = DEQARProfile.objects.create(user=self.user, submitting_agency=submitting_agency)
        self.deqar_profile.save()

        factory = RequestFactory()
        self.create_request = factory.post('/submissionapi/v2/submit/report')
        self.create_request.user = self.user


    def test_create_request_with_activity_group_id_and_agency(self):
        """
        Test if create serializer accepts a report with a group and agency specified.
        """
        data = self.valid_data
        data['activities'][0]['agency'] = 'EKKA'
        data['activities'].append({'id': '5'})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(len(serializer.validated_data['activities']), 2)

    def test_create_request_with_invalid_activity_group_id(self):
        """
            Test if create serializer rejects a report with an invalid group id.
        """
        data = self.valid_data
        data['activities'][0]['group'] = '100'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        with self.assertRaisesMessage(ValidationError, "Please provide valid ESG Activity Group Identifier."):
            serializer.is_valid(raise_exception=True)

    def test_create_request_with_invalid_activity_group_id_and_agency(self):
        """
            Test if create serializer rejects a report with an invalid group id.
        """
        data = self.valid_data
        data['activities'][0]['agency'] = 'EKKA'
        data['activities'][0]['group'] = '1'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        with self.assertRaisesMessage(ValidationError, "Please provide valid ESG Activity Group Identifier with Agency info."):
            serializer.is_valid(raise_exception=True)