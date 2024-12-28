from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.test import RequestFactory

from accounts.models import DEQARProfile
from agencies.models import SubmittingAgency
from submissionapi.v1.serializers.submisson_serializers import SubmissionPackageSerializer


class SubmissionAPIV1ReportTestWithAP(APITestCase):
    fixtures = ['agency_activity_type', 'agency_focus',
                'identifier_resource',
                'association',
                'country_historical_field',
                'country_qa_requirement_type', 'country',
                'language', 'qf_ehea_level',
                'report_decision', 'report_status',
                'flag', 'permission_type',
                'degree_outcome',
                'eter_demo',
                'eqar_decision_type',
                'agency_historical_field',
                'agency_demo_01', 'agency_demo_02',
                'assessment', 'institution_demo_01.yaml',
                'other_provider_01', 'other_provider_02',
                'users', 'submitting_agency_demo']

    def setUp(self):
        self.report_with_only_ap = {
            "agency": "ACQUIN",
            "valid_from": "2010-05-05",
            "date_format": "%Y-%M-%d",
            "activity": "1",
            "status": "2",
            "decision": "1",
            "report_files": [
                {
                    "report_language": ["eng"]
                }
            ],
            "institutions": [
                {
                    "deqar_id": "DEQARINSTAP0010",
                }
            ],
            "programmes": [
                {
                    "name_primary": "Programme name",
                    "degree_outcome": "2",
                    "workload_ects": 15,
                    "assessment_certification": "2",
                    "qf_ehea_level": "2",
                    "mc_as_part_of_accreditation": True,
                    "learning_outcomes": [
                        'http://data.europa.eu/esco/skill/04a13491-b58c-4d33-8b59-8fad0d55fe9e',
                        'http://data.europa.eu/esco/skill/cd9c487e-09ad-4b82-854b-118feb01f2ed'
                    ]
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
        self.request = factory.post('/submissionapi/v1/submit/report')
        self.request.user = self.user

    def test_base_package_is_ok(self):
        serializer = SubmissionPackageSerializer(data=self.report_with_only_ap, context={'request': self.request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    # status must be "voluntary" if all institutions are AP
    def test_status_is_voluntary_if_all_institutions_are_ap(self):
        data = self.report_with_only_ap
        data['status'] = "1"
        serializer = SubmissionPackageSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn("Status should be 'voluntary'", str(serializer.errors[settings.NON_FIELD_ERRORS_KEY]))

    def test_status_is_voluntary_if_one_of_the_institutions_is_ap(self):
        data = self.report_with_only_ap
        data['status'] = "1"
        data['activity'] = "3"
        data['institutions'].append({
            'deqar_id': 'DEQARINST0001'
        })
        serializer = SubmissionPackageSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    # programme degree outcome must be "no full degree" for only AP
    def test_degree_outcome_if_all_institutions_are_ap(self):
        data = self.report_with_only_ap
        data['programmes'][0]['degree_outcome'] = True
        serializer = SubmissionPackageSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn("Degree outcome should be '2 / no full degree'", str(serializer.errors[settings.NON_FIELD_ERRORS_KEY]))

    def test_degree_outcome_if_one_of_the_institutions_is_ap(self):
        data = self.report_with_only_ap
        data['activity'] = "3"
        data['institutions'].append({
            'deqar_id': 'DEQARINST0001'
        })
        data['programmes'][0]['degree_outcome'] = True
        serializer = SubmissionPackageSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    # additional programme data fields are required if degree outcome is "no full degree"
    def test_workload_ects_is_required_if_degree_outcome_is_false(self):
        data = self.report_with_only_ap
        programme01 = data['programmes'][0]
        del programme01['workload_ects']
        data['programmes'][0] = programme01
        serializer = SubmissionPackageSerializer(data=self.report_with_only_ap, context={'request': self.request})
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn("ECTS credits are required", str(serializer.errors))

    def test_assessment_is_required_if_degree_outcome_is_false(self):
        data = self.report_with_only_ap
        programme01 = data['programmes'][0]
        del programme01['assessment_certification']
        data['programmes'][0] = programme01
        serializer = SubmissionPackageSerializer(data=self.report_with_only_ap, context={'request': self.request})
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn("Assessment information is required", str(serializer.errors))

    def test_workload_ects_is_required_if_degree_outcome_is_false_with_multiple_programmes(self):
        data = self.report_with_only_ap
        data['programmes'].append(
            {
                "name_primary": "Programme name 2",
                "degree_outcome": "no",
                "assessment_certification": "2",
                "mc_as_part_of_accreditation": True
            }
        )
        serializer = SubmissionPackageSerializer(data=self.report_with_only_ap, context={'request': self.request})
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn("ECTS credits are required", str(serializer.errors))