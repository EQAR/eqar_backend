from django.contrib.auth.models import User
from django.test import RequestFactory
from rest_framework.test import APITestCase

from accounts.models import DEQARProfile
from agencies.models import SubmittingAgency
from submissionapi.v2.serializers.submisson_serializers import SubmissionPackageSerializer, \
    SubmissionPackageCreateSerializer, SubmissionPackageUpdateSerializer


class SubmissionV2ValidationTestCase(APITestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eter_demo', 'eqar_decision_type', 'language',
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
            "valid_from": "2010-05-05",
            "date_format": "%Y-%M-%d",
            "activities": [
                {
                    "activity": "1"
                }
            ],
            "status": "1",
            "decision": "1",
            "report_files": [
                {
                    "report_language": ["eng"]
                }
            ],
            "institutions": [
                {
                    "eter_id": "DE0392",
                    "identifiers": [
                        {
                            "identifier": "LOCAL001",
                            "resource": "local identifier"
                        }, {
                            "identifier": "DE0876",
                            "resource": "national identifier"
                        }
                    ]
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

        self.update_request = factory.put('/submissionapi/v2/submit/report')
        self.update_request.user = self.user


    def test_create_request_with_id(self):
        """
        Test if create serializer rejects a report_id.
        """
        data = self.valid_data
        data['report_id'] = '1'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_create_request_without_id(self):
        """
        Test if create serializer accepts a package without report_id.
        """
        data = self.valid_data
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_update_request_with_id(self):
        """
        Test if update serializer accepts a report_id.
        """
        data = self.valid_data
        data['report_id'] = '1'
        serializer = SubmissionPackageUpdateSerializer(data=data, context={'request': self.update_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_update_request_without_id(self):
        """
        Test if update serializer rejects a package without report_id.
        """
        data = self.valid_data
        serializer = SubmissionPackageUpdateSerializer(data=data, context={'request': self.update_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_update_request_with_report_id_non_existing(self):
        """
        Test if update serializer rejects a non existing report_id.
        """
        data = self.valid_data
        data['report_id'] = '999'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.update_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_request_without_programme_degree_outcome(self):
        """
        Test if update serializer rejects a report without programme.degree_outcome.
        """
        data = self.valid_data
        data['programmes'][0].pop('degree_outcome', None)
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_request_without_programme_qf_ehea_level(self):
        """
        Test if update serializer rejects a report without programme.qf_ehea_level.
        """
        data = self.valid_data
        data['programmes'][0].pop('qf_ehea_level', None)
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_acronym_ok(self):
        """
        Test if serializer accepts records with Agency Acronym.
        """
        serializer = SubmissionPackageCreateSerializer(data=self.valid_data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_agency_acronym_error(self):
        """
        Test if serializer rejects records with wrong Agency Acronym.
        """
        invalid_data = self.valid_data
        invalid_data['agency'] = 'ECQUIN'
        serializer = SubmissionPackageCreateSerializer(data=invalid_data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_deqar_id_ok(self):
        """
        Test if serializer accepts records with DEQAR ID.
        """
        valid_data = self.valid_data
        valid_data.pop('agency', None)
        valid_data['agency'] = "21"
        serializer = SubmissionPackageCreateSerializer(data=valid_data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_agency_deqar_id_error(self):
        """
        Test if serializer rejects records with wrong DEQAR ID.
        """
        invalid_data = self.valid_data
        invalid_data.pop('agency', None)
        invalid_data['agency'] = "999"
        serializer = SubmissionPackageCreateSerializer(data=invalid_data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_deqar_id_integer_error(self):
        """
        Test if serializer rejects records with wrong DEQAR ID.
        """
        invalid_data = self.valid_data
        invalid_data.pop('agency', None)
        invalid_data['agency'] = 21
        serializer = SubmissionPackageCreateSerializer(data=invalid_data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_esg_activity_id_validation_ok(self):
        """
        Test if serializer accepts records with ESG Activity ID.
        """
        serializer = SubmissionPackageCreateSerializer(data=self.valid_data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_agency_esg_activity_id_validation_error(self):
        """
        Test if serializer rejects records with wrong ESG Activity ID.
        """
        data = self.valid_data
        data['activities'] = [{"activity": 7}]
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_esg_activity_string__validation_error(self):
        """
        Test if serializer rejects records with wrong ESG Activity description.
        """
        data = self.valid_data
        data['activities'] = [{"activity": 'Programme Accreditation in Hungary'}]
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_esg_activity_local_identifier_validation_ok(self):
        """
        Test if serializer accepts records with ESG Activity local identifier.
        """
        data = self.valid_data
        data.pop('activity', None)
        data['activities'] = [{"local_identifier": 'ACQ001'}]
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_agency_esg_activity_local_identifier_validation_error(self):
        """
        Test if serializer rejects records with wrong ESG Activity local identifier.
        """
        data = self.valid_data
        data.pop('activity', None)
        data['activities'] = [{"local_identifier": 'ACQ999'}]
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_without_submitted_esg_activity(self):
        """
        Test if serializer rejects records if ESG Activity is not submitted.
        """
        data = self.valid_data
        data = data.pop('activities', None)
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_status_id_validation_ok(self):
        """
        Test if serializer accepts records with Report Status ID.
        """
        data = self.valid_data
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_status_id_validation_error(self):
        """
        Test if serializer rejects records with wrong Report Status ID.
        """
        data = self.valid_data
        data['status'] = 999
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_status_string_validation_ok(self):
        """
        Test if serializer accepts records with Report Status string.
        """
        data = self.valid_data
        data['status'] = 'part of obligatory EQA system'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_status_string_validation_error(self):
        """
        Test if serializer rejects records with wrong Report Status string.
        """
        data = self.valid_data
        data['status'] = 'is part of obligatory EQA system'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_decision_id_validation_ok(self):
        """
        Test if serializer accepts records with Report Decision ID.
        """
        data = self.valid_data
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_decision_id_validation_error(self):
        """
        Test if serializer accepts records with Report Decision ID.
        """
        data = self.valid_data
        data['decision'] = 999
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_decision_string_validation_ok(self):
        """
        Test if serializer accepts records with Report Decision string.
        """
        data = self.valid_data
        data['decision'] = 'positive with conditions or restrictions'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_decision_string_validation_error(self):
        """
        Test if serializer accepts records with Report Decision string.
        """
        data = self.valid_data
        data['decision'] = 'positive plus conditions or restrictions'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_date_format_custom_validation_ok(self):
        """
        Test if serializer accepts records with proper custom date format.
        """
        data = self.valid_data
        data['date_format'] = '%d-%m-%Y'
        data['valid_from'] = '03-04-2010'
        data['valid_to'] = '02-11-2015'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_date_format_default_validation_ok(self):
        """
        Test if serializer rejects records with proper default date format.
        """
        data = self.valid_data
        data['valid_from'] = '2010-04-10'
        data['valid_to'] = '2015-11-02'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_date_format_default_validation_error(self):
        """
        Test if serializer rejects records with proper default date format.
        """
        data = self.valid_data
        data['valid_from'] = '2010-04-10'
        data['valid_to'] = '2009-11-02'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_date_format_custom_validation_error(self):
        """
        Test if serializer rejects records with wrong custom date format.
        """
        data = self.valid_data
        data['date_format'] = '%d-%m-%Y'
        data['valid_from'] = '03-04-2010'
        data['valid_to'] = '03-13-2010'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_report_language_iso_639_1_ok(self):
        """
        Test if serializer accepts records with valid ISO 639-1 language codes.
        """
        data = self.valid_data
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_report_language_iso_639_1_error(self):
        """
        Test if serializer rejects records with wrong ISO 639-1 language codes.
        """
        data = self.valid_data
        data['report_files'][0].update({'report_language': ['zz']})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_report_language_iso_639_2_ok(self):
        """
        Test if serializer accepts records with valid ISO 639-2 language codes.
        """
        data = self.valid_data
        data['report_files'][0].update({'report_language': ['eng']})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_report_language_iso_639_2_error(self):
        """
        Test if serializer rejects records with wrong ISO 639-2 language codes.
        """
        data = self.valid_data
        data['report_files'][0].update({'report_language': ['zzz']})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_report_language_error(self):
        """
        Test if serializer rejects records with wrong language codes.
        """
        data = self.valid_data
        data['report_files'][0].update({'report_language': ['z']})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_eter_id_ok(self):
        """
        Test if serializer accepts records with ETER ID.
        """
        data = self.valid_data
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_eter_id_error(self):
        """
        Test if serializer rejects records with wrong ETER ID.
        """
        data = self.valid_data
        data['institutions'][0]['eter_id'] = '999'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_deqar_id_ok(self):
        """
        Test if serializer accepts records with DEQAR ID.
        """
        data = self.valid_data
        data['institutions'][0].pop('eter_id', None)
        data['institutions'][0]['deqar_id'] = 'DEQARINST0003'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_deqar_id_error(self):
        """
        Test if serializer rejects records with wrong DEQAR ID.
        """
        data = self.valid_data
        data['institutions'][0].pop('eter_id', None)
        data['institutions'][0]['deqar_id'] = 'DEQARINST9999'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_eter_id_and_deqar_id_match_ok(self):
        """
        Test if serializer accepts records with DEQAR ID and matching ETER ID.
        """
        data = self.valid_data
        data['institutions'][0]['deqar_id'] = 'DEQARINST0003'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_eter_id_and_deqar_id_match_error(self):
        """
        Test if serializer rejects records with DEQAR ID and non-matching ETER ID.
        """
        data = self.valid_data
        data['institutions'][0]['deqar_id'] = 'DEQARINST0001'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_identifiers_ok(self):
        """
        Test if serializer accepts records without DEQAR and ETER ID but with identifiers.
        """
        data = self.valid_data
        data['institutions'][0].pop('eter_id', None)
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_identifiers_error(self):
        """
        Test if serializer accepts records without DEQAR and ETER ID but with wrong identifiers.
        """
        data = self.valid_data
        data['institutions'][0].pop('eter_id', None)
        data['institutions'][0]['identifiers'][0]['identifier'] = 'NOT_EXISTING_LOCAL'
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)


    def test_institution_other_data_error(self):
        """
        Test if serializer rejects without DEQAR ID, ETER ID and identifiers but with name_official, location
        and missing website.
        """
        data = self.valid_data
        data['institutions'][0].pop('eter_id', None)
        data['institutions'][0].pop('identifiers', None)
        data['institutions'][0].update({
            'name_official': 'test',
            'locations': [
                {'country': 'deu'}
            ],
        })
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_resource_identifiers_ok(self):
        """
        Test if serializer accepts records with institution identifiers.
        """
        data = self.valid_data
        data['institutions'][0]['identifiers'].append({"identifier": "004"})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_resource_identifiers_two_id_without_resource_error(self):
        """
        Test if serializer rejects records with two institution identifiers without resource.
        """
        data = self.valid_data
        data['institutions'][0]['identifiers'].append({"identifier": "004"})
        data['institutions'][0]['identifiers'].append({"identifier": "124"})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_resource_identifiers_same_resources_error(self):
        """
        Test if serializer rejects records with two institution identifiers without resource.
        """
        data = self.valid_data
        data['institutions'][0]['identifiers'].append({"identifier": "004", "resource": "national identifier"})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_programme_qf_ehea_level_id_validation_ok(self):
        """
        Test if serializer accepts recrods with proper QF EHEA ID.
        """
        data = self.valid_data
        data['programmes'][0].update({'qf_ehea_level': '3'})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_programme_qf_ehea_level_id_validation_error(self):
        """
        Test if serializer rejects recrods with wrong QF EHEA ID.
        """
        data = self.valid_data
        data['programmes'][0].update({'qf_ehea_level': '99'})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_programme_qf_ehea_level_string_validation_ok(self):
        """
        Test if serializer accepts recrods with proper QF EHEA string.
        """
        data = self.valid_data
        data['programmes'][0].update({'qf_ehea_level': 'short cycle'})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_programme_qf_ehea_level_string_validation_error(self):
        """
        Test if serializer rejects recrods with wrong QF EHEA string.
        """
        data = self.valid_data
        data['programmes'][0].update({'qf_ehea_level': '1st cycle'})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_programme_country_alpha2_validation_ok(self):
        """
        Test if serializer accepts recrods with proper alpha2 country codes.
        """
        data = self.valid_data
        data['programmes'][0].update({'countries': ['DE', 'AT']})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_programme_country_alpha2_validation_error(self):
        """
        Test if serializer rejects recrods with wrong alpha2 country codes.
        """
        data = self.valid_data
        data['programmes'][0].update({'countries': ['DE', 'ZO']})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_programme_country_alpha3_validation_ok(self):
        """
        Test if serializer accepts recrods with proper alpha3 country codes.
        """
        data = self.valid_data
        data['programmes'][0].update({'countries': ['AUT', 'DEU']})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_programme_country_alpha3_validation_error(self):
        """
        Test if serializer rejects recrods with wrong alpha3 country codes.
        """
        data = self.valid_data
        data['programmes'][0].update({'countries': ['AUT', 'ZOO']})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_programme_country_badly_formatted_validation_error(self):
        """
        Test if serializer rejects recrods with badly formatted country codes.
        """
        data = self.valid_data
        data['programmes'][0].update({'countries': ['AUT', 'Z']})
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_report_esg_activity_institutional_ok(self):
        """
        Test if serializer accepts records with institutional ESG Activity type and valid data.
        """
        data = self.valid_data
        data['activities'] = [{"activity": "2"}]
        data.pop('programmes', None)
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_report_esg_activity_institutional_existing_programme_error(self):
        """
        Test if serializer rejects records with institutional ESG Activity type with programme data.
        """
        data = self.valid_data
        data['activities'] = [{"activity": "2"}]
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_report_esg_activity_programme_or_institutional_programme_ok(self):
        """
        Test if serializer accepts records with programme ESG Activity type and valid data.
        """
        data = self.valid_data
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_report_esg_activity_programme_or_institutional_programme_more_institution_error(self):
        """
        Test if serializer rejects records with programme ESG Activity type and data with many institutions.
        """
        data = self.valid_data
        data['institutions'].append({
            "eter_id": "DE0392"
        })
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_report_esg_activity_programme_or_institutional_programme_empty_programme_error(self):
        """
        Test if serializer rejects records with programme ESG Activity type and data without programme.
        """
        data = self.valid_data
        data.pop('programmes', None)
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_report_esg_activity_joint_programme_ok(self):
        """
        Test if serializer accepts records with joint programme ESG Activity type and valid data.
        """
        data = self.valid_data
        data['activities'] = [{"activity": "3"}]
        data['institutions'].append({
            "eter_id": "DE0392"
        })
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_report_esg_activity_joint_programme_one_institution_error(self):
        """
        Test if serializer rejects records with joint programme ESG Activity type and one institution.
        """
        data = self.valid_data
        data['activities'] = [{"activity": "3"}]
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_report_esg_activity_joint_programme_empty_programme_error(self):
        """
        Test if serializer rejects records with joint programme ESG Activity type and no programme data.
        """
        data = self.valid_data
        data['activities'] = [{"activity": "3"}]
        data['institutions'].append({
            "eter_id": "DE0392"
        })
        data.pop('programmes', None)
        serializer = SubmissionPackageCreateSerializer(data=data, context={'request': self.create_request})
        self.assertFalse(serializer.is_valid(), serializer.errors)