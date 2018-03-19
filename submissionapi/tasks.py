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
def send_submission_email(response, institution_id_max, total_submission, agency_email):
    from_email = getattr(settings, "EMAIL_FROM", "backend@deqar.eu")
    cc = getattr(settings, "EMAIL_CC", "")
    total_accepted = len(response)
    total_rejected = total_submission-total_accepted

    institution_existing = 0
    institution_new = 0

    for resp in response:
        for inst in resp['submitted_report']['institutions']:
            if inst['id'] > institution_id_max:
                institution_new += 1
            else:
                institution_existing += 1

    context = {
        'response': response,
        'total_submission': total_submission,
        'total_accepted': total_accepted,
        'total_rejected': total_rejected,
        'institution_total': institution_new + institution_existing,
        'institution_new': institution_new,
        'institution_existing': institution_existing,
        'max_inst_id': institution_id_max,
        'date': datetime.date.today().strftime("%Y-%m-%d"),
        'agency_email': agency_email
    }
    message = EmailMessage('email/submission.tpl', context=context,
                           from_email=from_email,
                           to=agency_email,
                           cc=cc)
    message.send()
