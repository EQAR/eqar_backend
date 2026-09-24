from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from django.test import SimpleTestCase

from agencies.tasks import (
    index_institutions_when_agency_acronym_changes,
    index_reports_when_agency_acronym_changes,
)


class AgencyReindexTaskTest(SimpleTestCase):

    @patch('agencies.tasks.meili_index_report.delay')
    @patch('agencies.tasks.ReportsIndexer')
    @patch('agencies.tasks.Report.objects.filter')
    def test_agency_name_change_reindexes_solr_and_meili_reports(
            self, mock_filter, mock_solr_indexer, mock_meili_index):
        reports = [SimpleNamespace(id=11), SimpleNamespace(id=12)]
        mock_filter.return_value.distinct.return_value.all.return_value = reports

        index_reports_when_agency_acronym_changes.run(5)

        self.assertEqual(mock_solr_indexer.call_args_list, [call(11), call(12)])
        for result in mock_solr_indexer.return_value.index.call_args_list:
            self.assertEqual(result, call())
        self.assertEqual(mock_solr_indexer.return_value.index.call_count, 2)
        self.assertEqual(mock_meili_index.call_args_list, [call(11, False), call(12, False)])

    @patch('agencies.tasks.MeiliInstitutionIndexer')
    @patch('agencies.tasks.InstitutionIndexer')
    @patch('agencies.tasks.Institution.objects.filter')
    def test_agency_name_change_reindexes_solr_and_meili_institutions(
            self, mock_filter, mock_solr_indexer, mock_meili_indexer):
        institutions = [SimpleNamespace(id=21), SimpleNamespace(id=22)]
        mock_filter.return_value.distinct.return_value.all.return_value = institutions

        index_institutions_when_agency_acronym_changes.run(5)

        self.assertEqual(mock_solr_indexer.call_args_list, [call(21), call(22)])
        self.assertEqual(mock_solr_indexer.return_value.index.call_count, 2)
        self.assertEqual(
            mock_meili_indexer.return_value.index.call_args_list,
            [call(21), call(22)],
        )
