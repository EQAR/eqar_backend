import mimetypes
import datetime

import os
import re
import requests
import functools
from django.conf import settings

from reports.models import ReportFile
from submissionapi.flaggers.report_flagger import ReportFlagger
from urllib.parse import unquote


class ReportDownloader:
    """
    Class to download files from report records.
    """
    def __init__(self, url, report_file_id, agency_acronym):
        self.url = unquote(url)
        self.report_file_id = report_file_id
        self.agency_acronym = agency_acronym
        self.old_file_path = ""
        self.saved_file_path = ""
        # session and HTTP defaults
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'DEQAR File Downloader'})
        self.session.request = functools.partial(self.session.request, timeout=getattr(settings, "REPORT_FILE_TIMEOUT", 5), allow_redirects=True)

    def download(self):
        if self._url_is_downloadable():
            file_name = self._get_filename()
            if file_name:
                self._get_old_file_path()
                self._download_file(local_filename=file_name)
                self._remove_old_file()

    def _get_old_file_path(self):
        rf = ReportFile.objects.get(pk=self.report_file_id)
        self.old_file_path = rf.file.name

    def _download_file(self, local_filename):
        r = self.session.get(self.url, stream=True)
        if r.status_code == requests.codes.ok:
            rf = ReportFile.objects.get(pk=self.report_file_id)
            file_path = os.path.join(settings.MEDIA_ROOT, self.agency_acronym, local_filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            self.saved_file_path = file_path

            if rf.file_display_name == "":
                rf.file_display_name = local_filename

            rf.file.name = os.path.join(self.agency_acronym, local_filename)
            rf.save()

            flagger = ReportFlagger(rf.report)
            flagger.check_and_set_flags()

    def _remove_old_file(self):
        if self.old_file_path != "":
            old_file = os.path.join(settings.MEDIA_ROOT, self.old_file_path)
            if os.path.exists(old_file):
                os.remove(old_file)

    def _url_is_downloadable(self):
        """
        Checks if url contain a downloadable resource
        """
        headers = {'User-Agent': 'DEQAR File Downloader'}
        h = self.session.head(self.url)

        if h.status_code != 200:
            return False

        header = h.headers
        content_type = header.get('content-type')

        # Fallback to GET if HEAD content-type is not application/pdf
        if content_type != 'application/pdf':
            r = self.session.get(self.url, stream=True)
            content_type = r.headers.get('content-type')
            if content_type != 'application/pdf':
                return False

        # Limit download to files less than 100MB
        content_length = header.get('content-length', None)
        if content_length and int(content_length) > 1e8:
            return False

        return True

    def _get_filename(self):
        """
        Detects filename from url. If URL doesn't contain filename, it checks
        content-disposition header. If that fails as well, it assigns the timestamp
        plus the extension according to the mime-type.
        """
        # Report file ID
        file_name = self.report_file_id

        # Step 1A. - Get content-disposition
        r = self.session.head(self.url)
        fn = self._get_filename_from_cd(r.headers.get('content-disposition'))

        # Step 1B. - Fallback to get request if head is not giving results.
        if not fn:
            r = self.session.get(self.url)
            fn = self._get_filename_from_cd(r.headers.get('content-disposition'))

        if fn:
            fn = fn.encode('iso-8859-1').decode('utf-8')

        # Step 2. - Get filename from url
        if not fn:
            fn = self.url.rsplit('/', 1)[1]
            fn, ext = os.path.splitext(fn)

            # Step 2A. - If filename is valid filename + extension in URL
            if fn != "" and ext != "":
                fn = "%s%s" % (fn, ext)

            # Step 2B. - If not add report_file_id + extension from Content-Type header
            else:
                ext = mimetypes.guess_extension(r.headers.get('Content-Type'))
                fn = "%s.%s" % (self.report_file_id, ext)

        return "%06d_%s_%s" % (file_name, datetime.datetime.now().strftime("%Y%m%d_%H%M"), fn)

    @staticmethod
    def _get_filename_from_cd(cd):
        """
        Get filename from content-disposition
        """
        if not cd:
            return None
        fname = re.findall('filename=(.+)', cd)
        if len(fname) == 0:
            return None
        else:
            fname = re.sub('\"|;', "", fname[0])
        return fname
