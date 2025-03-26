from django.test import TestCase

from unittest.mock import patch, MagicMock
from agencies.indexers.agency_indexer import AgencyIndexer
from agencies.models import Agency

class TestAgencyIndexer(TestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'flag',
        'agency_historical_field',
        'agency_activity_type', 'agency_focus', 'permission_type',
        'eqar_decision_type',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo'
    ]

    def setUp(self):
        agency = Agency.objects.get(pk=5)
        self.indexer = AgencyIndexer(agency)

    @patch('agencies.indexers.agency_indexer.pysolr.Solr.add')
    def test_index(self, mock_solr_add):
        self.indexer.index()
        mock_solr_add.assert_called_once()
        self.assertIn('id', self.indexer.doc)
        self.assertEqual(self.indexer.doc['id'], 5)

    def test_index_agency(self):
        self.indexer._index_agency()
        self.assertEqual(self.indexer.doc['id'], 5)
        self.assertEqual(self.indexer.doc['acronym'], 'ACQUIN')
        self.assertEqual(self.indexer.doc['name'], 'Accreditation, Certification and Quality Assurance Institute')
        self.assertEqual(self.indexer.doc['country'], 'Germany')
        self.assertEqual(self.indexer.doc['name_version_search'][1], 'Akkreditierungs-, Certifizierungs- und Qualitätssicherungsinstitut e.V.')
        self.assertIn('Hungary', self.indexer.doc['focus_country_facet'])

    def test_remove_duplicates(self):
        self.indexer.doc['name_version_search'] = ['name1', 'name1', 'name2']
        self.indexer._remove_duplicates()
        self.assertEqual(len(self.indexer.doc['name_version_search']), 2)

    def test_remove_empty_keys(self):
        self.indexer.doc['empty_key'] = []
        self.indexer.doc['non_empty_key'] = ['value']
        self.indexer._remove_empty_keys()
        self.assertNotIn('empty_key', self.indexer.doc)
        self.assertIn('non_empty_key', self.indexer.doc)
