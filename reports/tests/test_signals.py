from unittest.mock import patch

from django.db import transaction
from django.test import TestCase

from agencies.models import Agency
from reports.models import Report, ReportFile
from reports.signals import do_reharvest_file_when_location_change


class ReportFileReharvestSignalTest(TestCase):
    def setUp(self):
        self.old_url = 'https://example.com/original.pdf'
        self.report_file = ReportFile(
            id=406616,
            report=Report(agency=Agency(acronym_primary='NVAO')),
            file_original_location=self.old_url,
            file='NVAO/report.pdf',
            file_checksum='0123456789abcdef0123456789abcdef',
            download_status=ReportFile.DOWNLOAD_STATUS_SUCCESS,
        )
        # Exercise the production signal, which is normally disabled by manage.py test.
        argv = patch('reports.signals.sys.argv', ['manage.py'])
        argv.start()
        self.addCleanup(argv.stop)
        original = patch(
            'reports.signals.ReportFile.objects.get',
            return_value=ReportFile(file_original_location=self.old_url),
        )
        original.start()
        self.addCleanup(original.stop)
        download = patch('reports.signals.download_file.delay')
        self.download = download.start()
        self.addCleanup(download.stop)

    def trigger_signal(self):
        do_reharvest_file_when_location_change(ReportFile, self.report_file)

    def test_clearing_url_preserves_stored_file_without_downloading(self):
        self.report_file.file_original_location = ''

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            self.trigger_signal()

        self.assertEqual(callbacks, [])
        self.download.assert_not_called()
        self.assertEqual(self.report_file.download_status, ReportFile.DOWNLOAD_STATUS_SUCCESS)
        self.assertEqual(self.report_file.file.name, 'NVAO/report.pdf')
        self.assertEqual(self.report_file.file_checksum, '0123456789abcdef0123456789abcdef')

    def test_clearing_url_without_stored_file_does_not_download(self):
        self.report_file.file_original_location = ''
        self.report_file.file = ''

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            self.trigger_signal()

        self.assertEqual(callbacks, [])
        self.download.assert_not_called()
        self.assertEqual(self.report_file.download_status, '')

    def test_changed_url_downloads_after_commit_with_saved_arguments(self):
        new_url = 'https://example.com/replacement.pdf'
        self.report_file.file_original_location = new_url

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            self.trigger_signal()
            self.assertEqual(self.report_file.download_status, ReportFile.DOWNLOAD_STATUS_PENDING)
            self.download.assert_not_called()
            # Later changes to the instance must not change the queued task arguments.
            self.report_file.file_original_location = ''
            self.report_file.pk = 999
            self.report_file.report.agency.acronym_primary = 'OTHER'

        self.assertEqual(len(callbacks), 1)
        self.download.assert_called_once_with(new_url, 406616, 'NVAO')

    def test_rolled_back_url_change_does_not_download(self):
        self.report_file.file_original_location = 'https://example.com/replacement.pdf'

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            with self.assertRaises(RuntimeError):
                with transaction.atomic():
                    self.trigger_signal()
                    raise RuntimeError('Roll back the report update')

        self.assertEqual(callbacks, [])
        self.download.assert_not_called()

    def test_unchanged_url_does_not_download(self):
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            self.trigger_signal()

        self.assertEqual(callbacks, [])
        self.download.assert_not_called()
