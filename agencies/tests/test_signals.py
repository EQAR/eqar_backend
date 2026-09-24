from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from django.test import SimpleTestCase

from agencies.models import AgencyActivityGroup, AgencyActivityType, AgencyESGActivity
from agencies.signals import (
    do_index_reports_upon_activity_change,
    mark_reports_upon_activity_change,
    mark_reports_upon_activity_group_type_change,
    mark_reports_upon_activity_type_name_change,
)


class AgencyReindexSignalTest(SimpleTestCase):

    @patch('agencies.signals.meili_index_report.delay')
    @patch('agencies.signals.index_report.delay')
    @patch('agencies.signals.transaction.on_commit')
    @patch('agencies.signals.AgencyESGActivity.objects.get')
    @patch('agencies.signals.sys.argv', ['manage.py'])
    def test_activity_change_reindexes_solr_and_meili_after_commit(
            self, mock_get, mock_on_commit, mock_solr_index, mock_meili_index):
        original = SimpleNamespace(
            activity_display='Old display',
            activity='Old activity',
            activity_group_id=1,
        )
        reports = MagicMock()
        reports.values_list.return_value = [31, 32]
        changed = SimpleNamespace(
            id=7,
            activity_display='New display',
            activity='New activity',
            activity_group_id=2,
            reports=reports,
        )
        mock_get.return_value = original
        mock_on_commit.side_effect = lambda callback: callback()

        mark_reports_upon_activity_change(AgencyESGActivity, changed)

        mock_on_commit.assert_not_called()

        do_index_reports_upon_activity_change(AgencyESGActivity, changed)

        self.assertEqual(mock_on_commit.call_count, 4)
        self.assertEqual(mock_solr_index.call_args_list, [call(31), call(32)])
        self.assertEqual(mock_meili_index.call_args_list, [call(31), call(32)])

    @patch('agencies.signals.transaction.on_commit')
    @patch('agencies.signals.AgencyESGActivity.objects.get')
    @patch('agencies.signals.sys.argv', ['manage.py'])
    def test_unchanged_activity_does_not_schedule_reindex(self, mock_get, mock_on_commit):
        original = SimpleNamespace(
            activity_display='Display',
            activity='Activity',
            activity_group_id=1,
        )
        unchanged = SimpleNamespace(
            id=7,
            activity_display='Display',
            activity='Activity',
            activity_group_id=1,
            reports=MagicMock(),
        )
        mock_get.return_value = original

        mark_reports_upon_activity_change(AgencyESGActivity, unchanged)
        do_index_reports_upon_activity_change(AgencyESGActivity, unchanged)

        mock_on_commit.assert_not_called()

    @patch('agencies.signals.meili_index_report.delay')
    @patch('agencies.signals.index_report.delay')
    @patch('agencies.signals.transaction.on_commit')
    @patch('agencies.signals.Report.objects.filter')
    @patch('agencies.signals.AgencyActivityGroup.objects.get')
    @patch('agencies.signals.sys.argv', ['manage.py'])
    def test_activity_group_type_change_reindexes_affected_reports(
            self, mock_get, mock_filter, mock_on_commit, mock_solr_index, mock_meili_index):
        mock_get.return_value = SimpleNamespace(activity_type_id=1)
        mock_filter.return_value.values_list.return_value.distinct.return_value = [41]
        mock_on_commit.side_effect = lambda callback: callback()

        changed = SimpleNamespace(id=8, activity_type_id=2)
        mark_reports_upon_activity_group_type_change(AgencyActivityGroup, changed)
        do_index_reports_upon_activity_change(AgencyActivityGroup, changed)

        mock_solr_index.assert_called_once_with(41)
        mock_meili_index.assert_called_once_with(41)

    @patch('agencies.signals.meili_index_report.delay')
    @patch('agencies.signals.index_report.delay')
    @patch('agencies.signals.transaction.on_commit')
    @patch('agencies.signals.Report.objects.filter')
    @patch('agencies.signals.AgencyActivityType.objects.get')
    @patch('agencies.signals.sys.argv', ['manage.py'])
    def test_activity_type_name_change_reindexes_affected_reports(
            self, mock_get, mock_filter, mock_on_commit, mock_solr_index, mock_meili_index):
        mock_get.return_value = SimpleNamespace(type='programme')
        mock_filter.return_value.values_list.return_value.distinct.return_value = [51, 52]
        mock_on_commit.side_effect = lambda callback: callback()

        changed = SimpleNamespace(id=3, type='joint programme')
        mark_reports_upon_activity_type_name_change(AgencyActivityType, changed)
        do_index_reports_upon_activity_change(AgencyActivityType, changed)

        self.assertEqual(mock_solr_index.call_args_list, [call(51), call(52)])
        self.assertEqual(mock_meili_index.call_args_list, [call(51), call(52)])
