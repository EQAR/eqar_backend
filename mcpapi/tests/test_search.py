from django.core.management import call_command
from django.db.models import Q
from rest_framework.test import APITestCase

from agencies.models import Agency
from reports.models import Report

from mcpapi import tools
from mcpapi.exceptions import ToolInputError
from mcpapi.tests.test_tools import FIXTURES


class SearchToolTest(APITestCase):
    """
    search tools, running against the test Meilisearch indexes
    """
    fixtures = FIXTURES + ['other_provider_01', 'other_provider_02', 'report_demo_ap_01']

    def setUp(self):
        call_command('index_reports_meili', '--sync')
        call_command('index_institutions_meili', '--sync')

    def test_search_reports(self):
        visible = Report.objects.exclude(flag_id=tools.FLAG_HIGH_LEVEL_ID)
        result = tools.search_reports(limit=50)
        self.assertEqual(result['total'], visible.count())
        row = result['results'][0]
        for field in ['id', 'agency', 'decision', 'valid_from', 'deqar_url']:
            self.assertIn(field, row)

        agency = Agency.objects.get(acronym_primary='ACQUIN')
        by_agency = tools.search_reports(agency='ACQUIN', limit=0)
        self.assertEqual(by_agency['total'],
                         visible.filter(Q(agency=agency) | Q(contributing_agencies=agency)).distinct().count())
        self.assertEqual(by_agency['results'], [])

    def test_search_reports_facets(self):
        result = tools.search_reports(limit=0, include_facets=True)
        facets = result['facets']
        self.assertEqual(set(facets.keys()), {'agency', 'country', 'activity_type', 'decision', 'status'})
        # IDs are replaced by labels
        self.assertTrue(all(not label.isdigit() for label in facets['agency']))
        self.assertEqual(sum(facets['decision'].values()), result['total'])

    def test_search_reports_filters(self):
        # reports on the institution, possibly also on its sub-units and predecessors
        by_institution = tools.search_reports(institution='DEQARINST0001', limit=50)
        self.assertTrue(0 < by_institution['total'] < tools.search_reports(limit=0)['total'])
        self.assertTrue(any(1 in [i['id'] for i in row['institutions']] for row in by_institution['results']))

        positive = tools.search_reports(decision='positive', limit=50)
        self.assertTrue(all(r['decision'] == 'positive' for r in positive['results']))

        with self.assertRaisesRegex(ToolInputError, 'multiple of limit'):
            tools.search_reports(limit=10, offset=5)

    def test_search_institutions(self):
        result = tools.search_institutions(limit=50)
        self.assertTrue(result['total'] > 0)
        self.assertTrue(all('deqar_url' in i for i in result['results']))

        germany = tools.search_institutions(country='DE', limit=50)
        self.assertTrue(all(any(l.endswith('Germany') for l in i['locations']) for i in germany['results']))

        providers = tools.search_institutions(other_provider=True, limit=50)
        self.assertTrue(all(i.get('other_provider') for i in providers['results']))

    def test_get_institution(self):
        result = tools.get_institution('DEQARINST0001')
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['report_count'], tools.search_reports(institution='1', limit=0)['total'])
        self.assertNotIn('meili_filters', result)
        self.assertIsInstance(result['countries'][0]['country'], str)
