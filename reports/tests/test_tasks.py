from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from reports.tasks import meili_index_report


class ReportReindexTaskTest(SimpleTestCase):

    @patch('reports.tasks.MeiliInstitutionIndexer')
    @patch('reports.tasks.InstitutionIndexer')
    @patch('reports.tasks.ProgrammeIndexer')
    @patch('reports.tasks.MeiliReportIndexer')
    @patch('reports.tasks.Report.objects.get')
    def test_can_skip_institutions_when_they_are_reindexed_as_a_batch(
            self, mock_get, mock_report_indexer, mock_programme_indexer,
            mock_solr_institution_indexer, mock_meili_institution_indexer):
        report = SimpleNamespace(id=61, programme_set=MagicMock(), institutions=MagicMock())
        report.programme_set.iterator.return_value = []
        mock_get.return_value = report

        programme_indexer = mock_programme_indexer.return_value
        programme_indexer.meili.meili.index.return_value.get_documents.return_value.results = []

        meili_index_report.run(61, False)

        mock_report_indexer.return_value.index.assert_called_once_with(61)
        report.institutions.iterator.assert_not_called()
        mock_solr_institution_indexer.assert_not_called()
        mock_meili_institution_indexer.assert_not_called()
