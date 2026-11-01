from django.test import override_settings
from rest_framework.test import APITestCase

from agencies.models import Agency, AgencyActivityGroup
from countries.models import CountryQARequirementGroup, CountryQARequirement, CountryQAARegulation, \
    CountryInstitutionType, CountryIncomingTneRegulation, Country
from reports.models import Report, ReportFile

from mcpapi import resolvers, tools
from mcpapi.exceptions import ToolInputError
from mcpapi.shaping import prune, to_json, html_to_text

FIXTURES = ['agency_activity_type', 'agency_focus',
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


class ResolverTest(APITestCase):
    fixtures = FIXTURES

    def test_resolve_country(self):
        for value in ['64', 'DE', 'de', 'DEU', 'Germany', 'germany', ' Germany ']:
            self.assertEqual(resolvers.resolve_country(value).id, 64, value)

    def test_resolve_country_ambiguous_or_unknown(self):
        with self.assertRaisesRegex(ToolInputError, 'ambiguous country'):
            resolvers.resolve_country('land')
        with self.assertRaisesRegex(ToolInputError, 'unknown country'):
            resolvers.resolve_country('Narnia')
        with self.assertRaisesRegex(ToolInputError, 'unknown country'):
            resolvers.resolve_country('99999')

    def test_resolve_agency(self):
        agency = Agency.objects.get(acronym_primary='ACQUIN')
        for value in [str(agency.id), 'ACQUIN', 'acquin']:
            self.assertEqual(resolvers.resolve_agency(value), agency)
        with self.assertRaisesRegex(ToolInputError, 'unknown agency'):
            resolvers.resolve_agency('NO-SUCH-AGENCY')

    def test_resolve_institution(self):
        for value in ['1', 'DEQARINST0001', 'deqarinst0001']:
            self.assertEqual(resolvers.resolve_institution(value).id, 1, value)
        with self.assertRaisesRegex(ToolInputError, 'search_institutions'):
            resolvers.resolve_institution('Some University')

    def test_resolve_report_values(self):
        self.assertEqual(resolvers.resolve_report_decision('Positive').decision, 'positive')
        self.assertEqual(resolvers.resolve_language('en').language_name_en, 'English')
        with self.assertRaisesRegex(ToolInputError, 'unknown report status'):
            resolvers.resolve_report_status('bogus" OR 1=1')


class CountryToolTest(APITestCase):
    fixtures = FIXTURES

    def create_qa_framework(self):
        institution_type = CountryInstitutionType.objects.create(country_id=64, name_national='Universität',
                                                                 name_english='University', eter_category_standard=1)
        group = CountryQARequirementGroup.objects.create(country_id=64, combination_logic='OR', mc_possible=True,
                                                         mc_credit_limit=30, outgoing_tne_possible_id=2)
        group.institution_types.add(institution_type)
        activity_group = AgencyActivityGroup.objects.create(activity='Programme accreditation in Germany',
                                                            activity_type_id=1)
        requirement = CountryQARequirement.objects.create(group=group, activity_group=activity_group, duration=96,
                                                          cbqa_possible_id=3, ea_possible_id=1)
        requirement.qf_ehea_levels.add(2, 3)
        CountryQARequirement.objects.create(group=group, activity_group=activity_group,
                                            requirement_valid_to='2020-01-01')
        CountryQAARegulation.objects.create(country_id=64, regulation='Higher Education Act',
                                            regulation_url='https://www.example.org/act')
        CountryQAARegulation.objects.create(country_id=64, group=group, regulation='Studienakkreditierungsstaatsvertrag',
                                            regulation_url='https://www.akkreditierungsrat.de/')
        incoming = CountryIncomingTneRegulation.objects.create(country_id=64, incoming_tne_possible_id=2,
                                                               incoming_tne_qa_id=1)
        incoming.origin_groups.add(2)

    def test_list_countries(self):
        result = tools.list_countries()
        self.assertEqual(result['total'], Country.objects.filter(ehea_is_member=True).count())
        self.assertNotIn('url', result['results'][0])
        self.assertEqual(len(tools.list_countries(ehea_only=False)['results']), Country.objects.count())

        filtered = tools.list_countries(external_qaa='yes')['results']
        self.assertTrue(filtered)
        self.assertTrue(all(c['external_qaa_permitted'] == 'yes' for c in filtered))

    def test_get_country(self):
        self.create_qa_framework()
        result = tools.get_country('Germany')
        self.assertEqual(result['country']['iso2'], 'DE')
        self.assertIn('overview', result)
        self.assertEqual([r['regulation'] for r in result['qaa_regulations']], ['Higher Education Act'])

        group = result['qa_requirement_groups'][0]
        self.assertEqual(group['combination_logic'], 'OR')
        self.assertEqual(group['institution_types'][0]['category'], 'university')
        self.assertEqual(group['regulations'][0]['regulation'], 'Studienakkreditierungsstaatsvertrag')
        # controlled list entries collapsed to their title
        self.assertEqual(group['outgoing_tne_possible'], 'Yes, subject to conditions')
        self.assertEqual(result['incoming_tne_regulations'][0]['incoming_tne_possible'], 'Yes, subject to conditions')

        # expired requirement only with history; empty scope made explicit
        self.assertEqual(len(group['requirements']), 1)
        requirement = group['requirements'][0]
        self.assertEqual(requirement['qf_ehea_levels'], ['first cycle', 'second cycle'])
        self.assertEqual(requirement['fields_of_education'], 'all fields')
        self.assertEqual(requirement['cbqa_possible'], 'Allowed for all cases')
        history = tools.get_country('DE', include_history=True)
        self.assertEqual(len(history['qa_requirement_groups'][0]['requirements']), 2)

        self.assertNotIn('"url"', to_json(result))

    def test_get_country_sections(self):
        self.create_qa_framework()
        result = tools.get_country('64', sections=['microcredentials'])
        self.assertEqual(set(result.keys()), {'country', 'qa_requirement_groups'})
        group = result['qa_requirement_groups'][0]
        self.assertEqual(group['mc_credit_limit'], 30)
        self.assertNotIn('requirements', group)
        self.assertNotIn('outgoing_tne_possible', group)


class AgencyToolTest(APITestCase):
    fixtures = FIXTURES

    def test_search_agencies(self):
        result = tools.search_agencies(registered='all', limit=50)
        self.assertEqual(result['total'], Agency.objects.count())
        self.assertIsNone(result['next_offset'])

        page = tools.search_agencies(registered='all', limit=1)
        self.assertEqual(len(page['results']), 1)
        self.assertEqual(page['next_offset'], 1 if result['total'] > 1 else None)

        acquin = tools.search_agencies(query='acquin', registered='all')['results']
        self.assertEqual([a['acronym'] for a in acquin], ['ACQUIN'])

    def test_get_agency(self):
        result = tools.get_agency('ACQUIN', include=['activities', 'focus_countries', 'decisions', 'names'])
        self.assertEqual(result['acronym'], 'ACQUIN')
        self.assertIn('activities', result)
        self.assertIn('names', result)
        for private in ['contact_person', 'phone_numbers', 'emails', 'historical_data']:
            self.assertNotIn(private, result)

        default = tools.get_agency('ACQUIN')
        self.assertNotIn('names', default)
        self.assertNotIn('decisions', default)


class ReportToolTest(APITestCase):
    fixtures = FIXTURES

    @override_settings(MCP_PUBLIC_BASE_URL='https://backend.example.org')
    def test_get_report(self):
        ReportFile.objects.filter(report_id=1).update(file='ACQUIN/2018/report.pdf')
        result = tools.get_report(1)
        self.assertEqual(result['decision'], 'positive')
        self.assertEqual(result['contributing_agencies'][0]['acronym_primary'], 'EKKA')
        self.assertTrue(result['report_files'][0]['file'].startswith('https://backend.example.org/reports/'))
        self.assertIn('deqar_url', result)
        for hidden in ['agency_url', 'institutions_hierarchical', 'internal_note', 'flag_log']:
            self.assertNotIn(hidden, result)

        summary = tools.get_report(1, include_programmes=False)
        self.assertNotIn('programmes', summary)
        self.assertEqual(summary['programme_count'], len(result['programmes']))

    def test_get_report_hidden(self):
        Report.objects.filter(pk=1).update(flag_id=tools.FLAG_HIGH_LEVEL_ID)
        with self.assertRaisesRegex(ToolInputError, 'not found'):
            tools.get_report(1)

    def test_list_reference_values(self):
        self.assertEqual(tools.list_reference_values('report_decisions')['total'], 4)
        self.assertEqual(tools.list_reference_values('programme_types')['values'], list(tools.PROGRAMME_TYPES))
        languages = tools.list_reference_values('languages', query='engl')['values']
        self.assertIn('English', languages)


class ShapingTest(APITestCase):

    def test_prune(self):
        self.assertEqual(prune({'a': None, 'b': '', 'c': [], 'd': {}, 'e': False, 'f': 0, 'url': 'x',
                                'g': [None, {'h': ''}, 1]}),
                         {'e': False, 'f': 0, 'g': [1]})

    @override_settings(MCP_TEXT_MAX_CHARS=10)
    def test_truncate(self):
        self.assertTrue(prune('x' * 20).endswith('truncated]'))

    def test_html_to_text(self):
        self.assertEqual(html_to_text('<p>One&nbsp;para</p><p>See <a href="https://x.org">act</a></p>'),
                         'One para\n\nSee act (https://x.org)')
        self.assertEqual(html_to_text('a < b > c'), 'a < b > c')
