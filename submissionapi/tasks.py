import datetime
from celery.task import task
from django.conf import settings
from mail_templated import EmailMessage

from reports.models import Report
from submissionapi.downloaders.report_downloader import ReportDownloader
from submissionapi.flaggers.report_flagger import ReportFlagger


@task(name="download_file")
def download_file(url, report_file_id, agency_acronym):
    downloader = ReportDownloader(
        url=url,
        report_file_id=report_file_id,
        agency_acronym=agency_acronym
    )
    downloader.download()


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
                           to=[agency_email],
                           cc=cc)
    message.send()


@task(name="recheck_flag")
def recheck_flag(report_id):
    report = Report.objects.get(id=report_id)
    report_flagger = ReportFlagger(report)
    report_flagger.check_and_set_flags()