from rest_framework.test import APITestCase
from submissionapi.serializers import SubmissionPackageSerializer


class SubmissionValidationTestCase(APITestCase):
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

    def setUp(self):
        self.valid_data = {
            "agency": "ACQUIN",
            "valid_from": "2010-05-05",
            "date_format": "%Y-%M-%d",
            "activity": "1",
            "status": "1",
            "decision": "1",
            "report_files": [
                {
                    "report_language": "eng"
                }
            ],
            "institutions": [
                {
                    "eter_id": "DE0392",
                    "identifiers": [
                        {
                            "identifier": "004",
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
                    "name_primary": "Programme name"
                }
            ]
        }

    def test_agency_acronym_ok(self):
        """
        Test if serializer accepts records with Agency Acronym.
        """
        serializer = SubmissionPackageSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_agency_acronym_error(self):
        """
        Test if serializer rejects records with wrong Agency Acronym.
        """
        invalid_data = self.valid_data
        invalid_data['agency'] = 'ECQUIN'
        serializer = SubmissionPackageSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_deqar_id_ok(self):
        """
        Test if serializer accepts records with DEQAR ID.
        """
        valid_data = self.valid_data
        valid_data.pop('agency', None)
        valid_data['agency'] = 21
        serializer = SubmissionPackageSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_agency_deqar_id_error(self):
        """
        Test if serializer rejects records with wrong DEQAR ID.
        """
        invalid_data = self.valid_data
        invalid_data.pop('agency', None)
        invalid_data['agency'] = 999
        serializer = SubmissionPackageSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_esg_activity_id_validation_ok(self):
        """
        Test if serializer accepts records with ESG Activity ID.
        """
        serializer = SubmissionPackageSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_agency_esg_activity_id_validation_error(self):
        """
        Test if serializer rejects records with wrong ESG Activity ID.
        """
        data = self.valid_data
        data['activity'] = 6
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_esg_activity_string_validation_ok(self):
        """
        Test if serializer accepts records with ESG Activity description.
        """
        data = self.valid_data
        data['activity'] = 'Programme Accreditation in Germany'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_agency_esg_activity_string__validation_error(self):
        """
        Test if serializer rejects records with wrong ESG Activity description.
        """
        data = self.valid_data
        data['activity'] = 'Programme Accreditation in Hungary'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_esg_activity_local_identifier_validation_ok(self):
        """
        Test if serializer accepts records with ESG Activity local identifier.
        """
        data = self.valid_data
        data.pop('activity', None)
        data['activity_local_identifier'] = 'ACQ001'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_agency_esg_activity_local_identifier_validation_error(self):
        """
        Test if serializer rejects records with wrong ESG Activity local identifier.
        """
        data = self.valid_data
        data.pop('activity', None)
        data['activity_local_identifier'] = 'ACQ999'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_agency_without_submitted_esg_activity(self):
        """
        Test if serializer rejects records if ESG Activity is not submitted.
        """
        data = self.valid_data
        data = data.pop('activity', None)
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_status_id_validation_ok(self):
        """
        Test if serializer accepts records with Report Status ID.
        """
        data = self.valid_data
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_status_id_validation_error(self):
        """
        Test if serializer rejects records with wrong Report Status ID.
        """
        data = self.valid_data
        data['status'] = 999
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_status_string_validation_ok(self):
        """
        Test if serializer accepts records with Report Status string.
        """
        data = self.valid_data
        data['status'] = 'part of obligatory EQA system'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_status_string_validation_error(self):
        """
        Test if serializer rejects records with wrong Report Status string.
        """
        data = self.valid_data
        data['status'] = 'is part of obligatory EQA system'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_decision_id_validation_ok(self):
        """
        Test if serializer accepts records with Report Decision ID.
        """
        data = self.valid_data
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_decision_id_validation_error(self):
        """
        Test if serializer accepts records with Report Decision ID.
        """
        data = self.valid_data
        data['decision'] = 999
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_decision_string_validation_ok(self):
        """
        Test if serializer accepts records with Report Decision string.
        """
        data = self.valid_data
        data['decision'] = 'positive with conditions or restrictions'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_decision_string_validation_error(self):
        """
        Test if serializer accepts records with Report Decision string.
        """
        data = self.valid_data
        data['decision'] = 'positive plus conditions or restrictions'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_date_format_custom_validation_ok(self):
        """
        Test if serializer accepts records with proper custom date format.
        """
        data = self.valid_data
        data['date_format'] = '%d-%m-%Y'
        data['valid_from'] = '03-04-2010'
        data['valid_to'] = '02-11-2015'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_date_format_default_validation_ok(self):
        """
        Test if serializer rejects records with proper default date format.
        """
        data = self.valid_data
        data['valid_from'] = '2010-04-10'
        data['valid_to'] = '2015-11-02'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_date_format_custom_validation_error(self):
        """
        Test if serializer rejects records with wrong custom date format.
        """
        data = self.valid_data
        data['date_format'] = '%d-%m-%Y'
        data['valid_from'] = '03-04-2010'
        data['valid_to'] = '03-13-2010'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_country_alpha2_validation_ok(self):
        """
        Test if serializer accepts recrods with proper alpha2 country codes.
        """
        data = self.valid_data
        data['institutions'][0].update({'locations': [{'country': 'DE'}]})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_country_alpha2_validation_error(self):
        """
        Test if serializer accepts recrods with proper alpha2 country codes.
        """
        data = self.valid_data
        data['institutions'][0].update({'locations': [{'country': 'ZO'}]})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_country_alpha3_validation_ok(self):
        """
        Test if serializer accepts recrods with proper alpha3 country codes.
        """
        data = self.valid_data
        data['institutions'][0].update({'locations': [{'country': 'DEU'}]})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_country_alpha3_validation_error(self):
        """
        Test if serializer accepts recrods with proper alpha3 country codes.
        """
        data = self.valid_data
        data['institutions'][0].update({'locations': [{'country': 'ZOO'}]})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_country_badly_formatted_validation_error(self):
        """
        Test if serializer accepts recrods with badly formatted country codes.
        """
        data = self.valid_data
        data['institutions'][0].update({'locations': [{'country': 'Z'}]})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_qf_ehea_level_id_validation_ok(self):
        """
        Test if serializer accepts recrods with proper QF EHEA ID.
        """
        data = self.valid_data
        data['institutions'][0].update({'qf_ehea_levels': [{'qf_ehea_level': '3'}]})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_qf_ehea_level_id_validation_error(self):
        """
        Test if serializer rejects recrods with wrong QF EHEA ID.
        """
        data = self.valid_data
        data['institutions'][0].update({'qf_ehea_levels': [{'qf_ehea_level': '99'}]})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_qf_ehea_level_string_validation_ok(self):
        """
        Test if serializer accepts recrods with proper QF EHEA string.
        """
        data = self.valid_data
        data['institutions'][0].update({'qf_ehea_levels': [{'qf_ehea_level': 'short cycle'}]})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_qf_ehea_level_string_validation_error(self):
        """
        Test if serializer rejects recrods with wrong QF EHEA string.
        """
        data = self.valid_data
        data['institutions'][0].update({'qf_ehea_levels': [{'qf_ehea_level': '1st cycle'}]})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_report_language_iso_639_1_ok(self):
        """
        Test if serializer accepts records with valid ISO 639-1 language codes.
        """
        data = self.valid_data
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_report_language_iso_639_1_error(self):
        """
        Test if serializer rejects records with wrong ISO 639-1 language codes.
        """
        data = self.valid_data
        data['report_files'][0].update({'report_language': 'zz'})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_report_language_iso_639_2_ok(self):
        """
        Test if serializer accepts records with valid ISO 639-2 language codes.
        """
        data = self.valid_data
        data['report_files'][0].update({'report_language': 'eng'})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_report_language_iso_639_2_error(self):
        """
        Test if serializer rejects records with wrong ISO 639-2 language codes.
        """
        data = self.valid_data
        data['report_files'][0].update({'report_language': 'zzz'})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_report_language_error(self):
        """
        Test if serializer rejects records with wrong language codes.
        """
        data = self.valid_data
        data['report_files'][0].update({'report_language': 'z'})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_eter_id_ok(self):
        """
        Test if serializer accepts records with ETER ID.
        """
        data = self.valid_data
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_eter_id_error(self):
        """
        Test if serializer rejects records with wrong ETER ID.
        """
        data = self.valid_data
        data['institutions'][0]['eter_id'] = '999'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_deqar_id_ok(self):
        """
        Test if serializer accepts records with DEQAR ID.
        """
        data = self.valid_data
        data['institutions'][0].pop('eter_id', None)
        data['institutions'][0]['deqar_id'] = 'EQARIN0003'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_deqar_id_error(self):
        """
        Test if serializer rejects records with wrong DEQAR ID.
        """
        data = self.valid_data
        data['institutions'][0].pop('eter_id', None)
        data['institutions'][0]['deqar_id'] = 'EQARIN9999'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_eter_id_and_deqar_id_match_ok(self):
        """
        Test if serializer accepts records with DEQAR ID and matching ETER ID.
        """
        data = self.valid_data
        data['institutions'][0]['deqar_id'] = 'EQARIN0003'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_eter_id_and_deqar_id_match_error(self):
        """
        Test if serializer rejects records with DEQAR ID and non-matching ETER ID.
        """
        data = self.valid_data
        data['institutions'][0]['deqar_id'] = 'EQARIN0001'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_identifiers_ok(self):
        """
        Test if serializer accepts records without DEQAR and ETER ID but with identifiers.
        """
        data = self.valid_data
        data['institutions'][0].pop('eter_id', None)
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_other_data_ok(self):
        """
        Test if serializer accepts records without DEQAR ID, ETER ID and identifiers but with name_official, location
        and website.
        """
        data = self.valid_data
        data['institutions'][0].pop('eter_id', None)
        data['institutions'][0].pop('identifiers', None)
        data['institutions'][0].update({
            'name_official': 'test',
            'locations': [
                {'country': 'deu'}
            ],
            'website': 'http://www.example.com'
        })
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

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
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_resource_identifiers_ok(self):
        """
        Test if serializer accepts records with institution identifiers.
        """
        data = self.valid_data
        data['institutions'][0]['identifiers'].append({"identifier": "004"})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_resource_identifiers_two_id_without_resource_error(self):
        """
        Test if serializer rejects records with two institution identifiers without resource.
        """
        data = self.valid_data
        data['institutions'][0]['identifiers'].append({"identifier": "004"})
        data['institutions'][0]['identifiers'].append({"identifier": "124"})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_resource_identifiers_same_resources_error(self):
        """
        Test if serializer rejects records with two institution identifiers without resource.
        """
        data = self.valid_data
        data['institutions'][0]['identifiers'].append({"identifier": "004", "resource": "national identifier"})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_name_official_transliteration_error(self):
        """
        Test if serializer rejects records with only name_official_transliteration submitted.
        """
        data = self.valid_data
        data['institutions'][0]['name_official_transliterated'] = 'Institution Name'
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_name_alternative_ok(self):
        """
        Test if serializer accepts records with valid alternative name submitted.
        """
        data = self.valid_data
        data['institutions'][0]['alternative_names'] = [{
                'name_alternative': 'alternative_name',
                'name_alternative_transliterated': 'alternative_name_transliterated'
        }]
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_name_alternative_error(self):
        """
        Test if serializer rejects records with invalid alternative name submitted.
        """
        data = self.valid_data
        data['institutions'][0]['alternative_names'] = [{
                'name_alternative_transliterated': 'alternative_name_transliterated'
        }]
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_country_latitude_and_longitude_ok(self):
        """
        Test if serializer accepts records with city, plus latitude and longitude.
        """
        data = self.valid_data
        data['institutions'][0]['locations'] = [{
                'country': 'deu',
                'city': 'Munich',
                'latitude': '48.137154',
                'longitude': '11.576124'
        }]
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_institution_country_latitude_without_longitude_error(self):
        """
        Test if serializer rejects records with city and latitude without longitude.
        """
        data = self.valid_data
        data['institutions'][0]['locations'] = [{
                'country': 'deu',
                'city': 'Munich',
                'latitude': '48.137154',
        }]
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_country_without_latitude_and_with_longitude_error(self):
        """
        Test if serializer rejects records with city without latitude with longitude.
        """
        data = self.valid_data
        data['institutions'][0]['locations'] = [{
                'country': 'deu',
                'city': 'Munich',
                'longitude': '11.576124',
        }]
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_institution_without_country_with_latitude_and_longitude_error(self):
        """
        Test if serializer rejects records without city but with latitude without longitude.
        """
        data = self.valid_data
        data['institutions'][0]['locations'] = [{
                'country': 'deu',
                'latitude': '48.137154',
                'longitude': '11.576124'
        }]
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_programme_qf_ehea_level_id_validation_ok(self):
        """
        Test if serializer accepts recrods with proper QF EHEA ID.
        """
        data = self.valid_data
        data['programmes'][0].update({'qf_ehea_level': '3'})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_programme_qf_ehea_level_id_validation_error(self):
        """
        Test if serializer rejects recrods with wrong QF EHEA ID.
        """
        data = self.valid_data
        data['programmes'][0].update({'qf_ehea_level': '99'})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_programme_qf_ehea_level_string_validation_ok(self):
        """
        Test if serializer accepts recrods with proper QF EHEA string.
        """
        data = self.valid_data
        data['programmes'][0].update({'qf_ehea_level': 'short cycle'})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_programme_qf_ehea_level_string_validation_error(self):
        """
        Test if serializer rejects recrods with wrong QF EHEA string.
        """
        data = self.valid_data
        data['institutions'][0].update({'qf_ehea_levels': '1st cycle'})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_programme_country_alpha2_validation_ok(self):
        """
        Test if serializer accepts recrods with proper alpha2 country codes.
        """
        data = self.valid_data
        data['programmes'][0].update({'countries': ['DE', 'AT']})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_programme_country_alpha2_validation_error(self):
        """
        Test if serializer rejects recrods with wrong alpha2 country codes.
        """
        data = self.valid_data
        data['programmes'][0].update({'countries': ['DE', 'ZO']})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_programme_country_alpha3_validation_ok(self):
        """
        Test if serializer accepts recrods with proper alpha3 country codes.
        """
        data = self.valid_data
        data['programmes'][0].update({'countries': ['AUT', 'DEU']})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_programme_country_alpha3_validation_error(self):
        """
        Test if serializer rejects recrods with wrong alpha3 country codes.
        """
        data = self.valid_data
        data['programmes'][0].update({'countries': ['AUT', 'ZOO']})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_programme_country_badly_formatted_validation_error(self):
        """
        Test if serializer rejects recrods with badly formatted country codes.
        """
        data = self.valid_data
        data['programmes'][0].update({'countries': ['AUT', 'Z']})
        serializer = SubmissionPackageSerializer(data=data)
        self.assertFalse(serializer.is_valid(), serializer.errors)