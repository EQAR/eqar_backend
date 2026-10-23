from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from agencies.models import AgencyActivityGroup
from countries.models import CountryQARequirementGroup, CountryQARequirement, CountryQAARegulation, \
    CountryInstitutionType, CountryIncomingTneRegulation


class BrowseCountryAPITest(APITestCase):
    fixtures = ['agency_activity_type', 'agency_focus',
                'identifier_resource',
                'association',
                'country', 'country_qa_lists',
                'language', 'qf_ehea_level',
                'report_decision', 'report_status',
                'flag', 'permission_type', 'degree_outcome',
                'eqar_decision_type',
                'agency_historical_field',
                'agency_demo_01', 'agency_demo_02',
                'institution_historical_field',
                'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
                'users', 'report_demo_01',
                'programme_demo_01', 'programme_demo_02', 'programme_demo_03', 'programme_demo_04',
                'programme_demo_05', 'programme_demo_06', 'programme_demo_07', 'programme_demo_08',
                'programme_demo_09', 'programme_demo_10', 'programme_demo_11', 'programme_demo_12']

    def setUp(self):
        self.user = User.objects.create_superuser(username='testuser',
                                                  email='testuser@eqar.eu',
                                                  password='testpassword')
        self.user.save()
        self.token = Token.objects.get(user__username='testuser')

    def test_country_list(self):
        """
            Test if we can display a list of countries.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/countries/')
        self.assertEqual(len(response.data), 49)

    def test_country_list_external_qaa_filter(self):
        """
            Test if we can display a list of countries with the external QAA filter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response_1 = self.client.get('/webapi/v2/browse/countries/', {'external_qaa': 1})
        self.assertEqual(response_1.data[0]['name_english'], 'Armenia')

        response_2 = self.client.get('/webapi/v2/browse/countries/', {'external_qaa': 2})
        self.assertEqual(len(response_2.data), 32)

        response_3 = self.client.get('/webapi/v2/browse/countries/', {'external_qaa': 3})
        self.assertEqual(response_3.data[0]['name_english'], 'Albania')

    def test_country_list_european_approach_filter(self):
        """
            Test if we can display a list of countries with the external QAA filter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response_1 = self.client.get('/webapi/v2/browse/countries/', {'european_approach': 1})
        self.assertEqual(response_1.data[0]['name_english'], 'Armenia')

        response_2 = self.client.get('/webapi/v2/browse/countries/', {'european_approach': 2})
        self.assertEqual(response_2.data[0]['name_english'], 'Albania')

        response_3 = self.client.get('/webapi/v2/browse/countries/', {'european_approach': 3})
        self.assertEqual(len(response_3.data), 0)

    def test_country_list_eqar_governmental_member(self):
        """
            Test if we can display a list of countries with the EQAR govermental member filter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response_true = self.client.get('/webapi/v2/browse/countries/', {'eqar_governmental_member': 'true'})
        self.assertEqual(len(response_true.data), 38)

        response_false = self.client.get('/webapi/v2/browse/countries/', {'eqar_governmental_member': 'false'})
        self.assertEqual(len(response_false.data), 11)

    def test_country_detail(self):
        """
            Test if we can display a particular country.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/countries/64/')
        self.assertEqual(response.data['name_english'], 'Germany')
        self.assertNotIn('historical_data', response.data)

    def test_country_detail_with_history(self):
        """
            Test if we can display a particular country with history.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/countries/64/', {'history': 'true'})
        self.assertEqual(response.data['name_english'], 'Germany')

    def test_country_detail_qa_requirement_groups(self):
        """
            Test if the structured QA requirements, TNE and micro-credential information is displayed.
        """
        institution_type = CountryInstitutionType.objects.create(country_id=64, name_national='Universität',
                                                                 name_english='University')
        group = CountryQARequirementGroup.objects.create(country_id=64, combination_logic='OR', mc_possible=True,
                                                         mc_credit_limit=30, outgoing_tne_possible_id=2)
        group.institution_types.add(institution_type)
        group.mc_qa.add(1, 2)
        activity_group = AgencyActivityGroup.objects.create(activity='Programme accreditation in Germany',
                                                            activity_type_id=1)
        requirement = CountryQARequirement.objects.create(group=group, activity_group=activity_group, duration=96,
                                                          fields_of_education=['http://data.europa.eu/esco/isced-f/0321'],
                                                          cbqa_possible_id=3, cbqa_criteria_id=2,
                                                          cbqa_recognition_id=2, ea_possible_id=1)
        requirement.qf_ehea_levels.add(2, 3)
        requirement.cbqa_requirements.add(1)
        CountryQARequirement.objects.create(group=group, activity_group=activity_group,
                                            requirement_valid_to='2020-01-01')
        CountryQAARegulation.objects.create(country_id=64, group=group, regulation='Studienakkreditierungsstaatsvertrag',
                                            regulation_url='https://www.akkreditierungsrat.de/')
        incoming = CountryIncomingTneRegulation.objects.create(country_id=64, incoming_tne_possible_id=2,
                                                               incoming_tne_qa_id=1)
        incoming.origin_groups.add(2, 3)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/countries/64/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data['qa_requirement_groups']), 1)
        group_data = response.data['qa_requirement_groups'][0]
        self.assertEqual(group_data['combination_logic'], 'OR')
        self.assertEqual(group_data['institution_types'][0]['name_english'], 'University')
        self.assertEqual(group_data['outgoing_tne_possible']['title'], 'Yes, subject to conditions')
        self.assertEqual([mc['id'] for mc in group_data['mc_qa']], [1, 2])
        self.assertEqual(group_data['regulations'][0]['regulation'], 'Studienakkreditierungsstaatsvertrag')

        # expired requirement is only shown with history
        self.assertEqual(len(group_data['requirements']), 1)
        requirement_data = group_data['requirements'][0]
        self.assertEqual(requirement_data['activity_group']['activity'], 'Programme accreditation in Germany')
        self.assertEqual(requirement_data['activity_group']['activity_type'], 'programme')
        self.assertEqual(requirement_data['duration'], 96)
        self.assertEqual(requirement_data['fields_of_education'], ['http://data.europa.eu/esco/isced-f/0321'])
        self.assertEqual(requirement_data['qf_ehea_levels'], ['first cycle', 'second cycle'])
        self.assertEqual(set(requirement_data['cbqa_possible'].keys()), {'id', 'title', 'uri', 'description'})
        self.assertEqual(requirement_data['cbqa_possible']['title'], 'Allowed for all cases')
        self.assertEqual(requirement_data['cbqa_requirements'][0]['title'], 'EQAR registration')
        self.assertEqual(requirement_data['ea_possible']['title'], 'Yes, without restrictions')

        self.assertEqual(response.data['incoming_tne_regulations'][0]['incoming_tne_possible']['title'],
                         'Yes, subject to conditions')
        self.assertEqual([g['title'] for g in response.data['incoming_tne_regulations'][0]['origin_groups']],
                         ['Non-EU EHEA members', 'Non-EHEA countries'])
        self.assertIn('lrc_signatory_date', response.data)
        self.assertNotIn('qa_requirements', response.data)

        response = self.client.get('/webapi/v2/browse/countries/64/', {'history': 'true'})
        self.assertEqual(len(response.data['qa_requirement_groups'][0]['requirements']), 2)

    def test_country_reports_list(self):
        """
            Test if we can display a list of countries by reports.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/countries/by-reports/')
        self.assertEqual(len(response.data), 1)

    def test_country_reports_list_with_history(self):
        """
            Test if we can display a list of countries by reports with historical data.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/countries/by-reports/', {'history': 'true'})
        self.assertEqual(len(response.data), 3)
