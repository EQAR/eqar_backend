import unittest
from unittest.mock import patch, MagicMock
from agencies.indexers.agency_indexer import AgencyIndexer
from agencies.models import Agency
from countries.models import Country

class TestAgencyIndexer(unittest.TestCase):

    def setUp(self):
        self.country = Country(id=1, name_english='Germany')
        self.agency = Agency(
            id=1,
            acronym_primary='ACQUIN',
            name_primary='Accreditation, Certification and Quality Assurance Institute',
            country=self.country,
            registration_start='2020-01-01',
            registration_valid_to='2025-01-01'
        )
        self.indexer = AgencyIndexer(self.agency)

    @patch('agencies.indexers.agency_indexer.pysolr.Solr.add')
    def test_index(self, mock_solr_add):
        self.indexer.index()
        mock_solr_add.assert_called_once()
        self.assertIn('id', self.indexer.doc)
        self.assertEqual(self.indexer.doc['id'], 1)

    def test_index_agency(self):
        self.indexer._index_agency()
        self.assertEqual(self.indexer.doc['id'], 1)
        self.assertEqual(self.indexer.doc['acronym'], 'ACQUIN')
        self.assertEqual(self.indexer.doc['name'], 'Accreditation, Certification and Quality Assurance Institute')
        self.assertEqual(self.indexer.doc['country'], 'Germany')

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
