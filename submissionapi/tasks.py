import datetime
import os
import requests
from celery.task import task
from django.conf import settings
from mail_templated import EmailMessage

from reports.models import ReportFile
from submissionapi.flaggers.report_flagger import ReportFlagger


@task(name="download_file")
def download_file(url, report_file_id, agency_acronym):
    local_filename = url.split('/')[-1]
    local_filename = "%s_%s" % ((datetime.datetime.now().strftime("%Y%m%d_%H%M")), local_filename)
    r = requests.get(url, stream=True)
    if r.status_code == requests.codes.ok:
        rf = ReportFile.objects.get(pk=report_file_id)
        file_path = os.path.join(settings.MEDIA_ROOT, agency_acronym, local_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        rf.file.name = os.path.join(agency_acronym, local_filename)
        rf.save()

        flagger = ReportFlagger(rf.report)
        flagger.check_and_set_flags()


@task(name="send_submission_email")
def send_submission_email(response, agency_email):
    from_email = getattr(settings, "EMAIL_FROM", "backend@deqar.eu")
    cc = getattr(settings, "EMAIL_CC", "")
    to_email = getattr(settings, "EMAIL_TO", "")
    context = {
        'response': response,
        'date': datetime.date.today().strftime("%Y-%m-%d"),
        'agency_email': agency_email
    }
    message = EmailMessage('email/submission.tpl', context=context,
                           from_email=from_email,
                           to=to_email,
                           cc=cc)
    message.send()
