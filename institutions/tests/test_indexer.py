import sys
from io import StringIO
from unittest.mock import patch, MagicMock

import pysolr
from django.test import TestCase

from countries.models import Country
from institutions.indexers.institution_indexer import InstitutionIndexer
from institutions.models import Institution

class TestInstitutionIndexer(TestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'flag', 'permission_type',
        'qf_ehea_level', 'institution_historical_field',
        'agency_activity_type', 'agency_focus', 'identifier_resource',
        'agency_historical_field',
        'eqar_decision_type',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03', 'institution_demo_closed',
        'institution_relationship_type', 'institution_hierarchical_relationship_type'
    ]

    def setUp(self):
        self.country = Country.objects.get(name_english='Germany')
        self.institution = Institution.objects.get(id=1)
        self.indexer = InstitutionIndexer(self.institution.id)

    @patch('institutions.indexers.institution_indexer.pysolr.Solr.add')
    def test_indexes_institution_successfully(self, mock_solr_add):
        self.indexer.index()
        mock_solr_add.assert_called_once()
        self.assertEqual(self.indexer.doc['id'], self.institution.id)
        self.assertEqual(self.indexer.doc['deqar_id'], self.institution.deqar_id)

    @patch('institutions.indexers.institution_indexer.pysolr.Solr.add')
    def test_handles_solr_error_gracefully(self, mock_solr_add):
        captured_output = StringIO()  # Make StringIO.
        sys.stdout = captured_output

        mock_solr_add.side_effect = pysolr.SolrError("Solr error")
        self.indexer.index()
        mock_solr_add.assert_called_once()

        sys.stdout = sys.__stdout__
        self.assertEqual("Error with Institution No. 1! Error: Solr error\n", captured_output.getvalue())

    def test_removes_duplicates_from_doc(self):
        self.indexer.doc['name_english'] = ['name1', 'name1', 'name2']
        self.indexer._remove_duplicates()
        self.assertEqual(len(self.indexer.doc['name_english']), 2)

    def test_removes_empty_keys_from_doc(self):
        self.indexer.doc['empty_key'] = []
        self.indexer.doc['non_empty_key'] = ['value']
        self.indexer._remove_empty_keys()
        self.assertNotIn('empty_key', self.indexer.doc)
        self.assertIn('non_empty_key', self.indexer.doc)

    @patch('institutions.indexers.institution_indexer.Institution.objects.get')
    def test_gets_institution_by_id(self, mock_get):
        mock_get.return_value = self.institution
        self.indexer._get_institution()
        mock_get.assert_called_once_with(pk=self.institution.id)
        self.assertEqual(self.indexer.institution, self.institution)
