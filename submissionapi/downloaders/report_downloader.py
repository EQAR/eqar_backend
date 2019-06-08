import mimetypes
import datetime

import os
import re
import requests
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
        headers = {'User-Agent': 'DEQAR File Downlaoder'}
        r = requests.get(self.url, headers=headers, stream=True, allow_redirects=True)
        if r.status_code == requests.codes.ok:
            rf = ReportFile.objects.get(pk=self.report_file_id)
            file_path = os.path.join(settings.MEDIA_ROOT, self.agency_acronym, local_filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            self.saved_file_path = file_path
            rf.file.name = os.path.join(self.agency_acronym, local_filename)
            rf.save()

            flagger = ReportFlagger(rf.report)
            flagger.check_and_set_flags()

    def _remove_old_file(self):
        if self.old_file_path != "":
            os.remove(os.path.join(settings.MEDIA_ROOT, self.old_file_path))

    def _url_is_downloadable(self):
        """
        Checks if url contain a downloadable resource
        """
        headers = {'User-Agent': 'DEQAR File Downlaoder'}
        h = requests.head(self.url, headers=headers, allow_redirects=True)

        header = h.headers
        content_type = header.get('content-type')
        if 'text' in content_type.lower():
            return False
        if 'html' in content_type.lower():
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
        r = requests.get(self.url, allow_redirects=True)

        # Current datetime
        file_name = datetime.datetime.now().strftime("%Y%m%d_%H%M")

        # Get filename from url
        fn = self.url.rsplit('/', 1)[1]
        if fn != "":
            fn, ext = os.path.splitext(fn)
            # If filename is valid filename + extension in URL
            if fn != "" and ext != "":
                file_name += "_%s%s" % (fn, ext)
            # If not add report_file_id + extension from Content-Type header
            else:
                ext = mimetypes.guess_extension(r.headers.get('Content-Type'))
                file_name += "_%s.%s" % (self.report_file_id, ext)
        else:
            # Get content-disposition
            file_name += "_%s" % self._get_filename_from_cd(r.headers.get('content-disposition'))

        return file_name

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
        return fname[0]
