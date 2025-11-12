import hashlib
import mimetypes
import datetime
import filetype

import os
import re
import requests
import functools
from django.conf import settings
from django.core.management import color_style

from reports.models import ReportFile
from urllib.parse import unquote, urlparse
from email.message import Message


class FileTooLarge(Exception):
    """
    File at URL exceeds the 100MB limit
    """
    pass

class WrongFileType(Exception):
    """
    File at URL was downloaded but is not a PDF
    """
    pass

class RetryHTTPError(requests.HTTPError):
    """
    HTTP 500+ or 429 (rate limit) error - for this one, retry is useful
    """
    pass

class ReportDownloader:
    """
    Class to download files from report records.
    """
    def __init__(self, url, report_file_id, agency_acronym):
        self.url = unquote(url)
        self.report_file = ReportFile.objects.get(pk=report_file_id)
        self.agency_acronym = agency_acronym
        # colourful logging
        self.style = color_style()
        # check data of existing file
        if self.report_file.file:
            self.old_file_path = self.report_file.file.name
            self.old_checksum = self.report_file.file_checksum
        else:
            self.old_file_path = None
            self.old_checksum = None
        self.saved_file_path = None
        # session and HTTP defaults
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'DEQAR File Downloader'})
        self.session.request = functools.partial(self.session.request, timeout=getattr(settings, "REPORT_FILE_TIMEOUT", 5), allow_redirects=True)


    def download(self):
        r = self.session.get(self.url, stream=True)

        try:
            r.raise_for_status()
        except requests.HTTPError as exc:
            if r.status_code >= requests.codes.server_error or r.status_code == requests.codes.too_many_requests:
                # server-side error or rate-limiting: custom exception that triggers a retry
                raise RetryHTTPError(request=exc.request, response=exc.response) from exc
            else:
                raise exc

        if r.status_code == requests.codes.ok:
            # Limit download to files less than 100MB
            content_length = r.headers.get('content-length', None)
            if content_length and int(content_length) > 1e8:
                raise FileTooLarge

            # determine local filename
            local_filename = self._get_filename(r)

            # download the file
            self.saved_file_name = os.path.join(self.agency_acronym, local_filename)
            self.saved_file_path = os.path.join(settings.MEDIA_ROOT, self.saved_file_name)
            os.makedirs(os.path.dirname(self.saved_file_path), exist_ok=True)
            with open(self.saved_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            # check content-type
            content_type = r.headers.get('content-type')
            if content_type != 'application/pdf':
                ft = filetype.guess(self.saved_file_path)
                if ft is None or ft.mime != 'application/pdf':
                    os.remove(self.saved_file_path)
                    raise WrongFileType
                else:
                    print(self.style.WARNING(f'Report {self.report_file.report.id} / File {self.report_file.id}: {self.url} reported wrong content type {content_type}, but downloaded file is a PDF'))

            if self.report_file.file_display_name == "":
                self.report_file.file_display_name = local_filename

            # Check if the downloaded file is different from the old file
            with open(self.saved_file_path, 'rb') as f:
                checksum = hashlib.md5(f.read()).hexdigest()

            # If the two checksums are different, update the file and remove the old one,
            # if they are identical remove the downloaded file
            if checksum != self.old_checksum:
                self.report_file.file.name = self.saved_file_name
                self.report_file.save()
                self._remove_old_file()
                print(self.style.SUCCESS(f'Report {self.report_file.report.id} / File {self.report_file.id}: saved file downloaded from {self.url}'))
            else:
                os.remove(self.saved_file_path)
                print(self.style.WARNING(f'Report {self.report_file.report.id} / File {self.report_file.id}: file downloaded from {self.url} has identical checksum, discarded'))


    def _remove_old_file(self):
        if self.old_file_path:
            old_file = os.path.join(settings.MEDIA_ROOT, self.old_file_path)
            if os.path.exists(old_file):
                os.remove(old_file)

    def _get_filename(self, response):
        """
        Detects filename from content-disposition header or URL.
        """

        # Option 1: get content-disposition
        filename = self._get_filename_from_cd(response.headers.get('content-disposition'))

        if filename:
            filename = filename.encode('iso-8859-1').decode('utf-8')

        # Option 2: use URL
        if not filename:
            filename = urlparse(self.url).path.rsplit('/', 1)[1]

        # Fallback
        if not filename:
            filename = 'document'

        # Ensure PDF extension
        filename, ext = os.path.splitext(filename)
        filename += '.pdf'

        return "%06d_%s_%s" % (self.report_file.id, datetime.datetime.now().strftime("%Y%m%d_%H%M"), filename)

    @staticmethod
    def _get_filename_from_cd(cd):
        """
        Get filename from content-disposition
        """
        m = Message()
        m['content-type'] = cd # not a mistake, the content-type header is parsed by get_param(s)
        return m.get_param('filename')

