import datetime
import logging
import traceback
from tempfile import template

from celery.task import task
from django.conf import settings
from django.core.mail import mail_admins
from mail_templated import EmailMessage
import requests

from reports.models import ReportFile
from submissionapi.downloaders.report_downloader import ReportDownloader, RetryHTTPError
from submissionapi.flaggers.report_flagger import ReportFlagger

logger = logging.getLogger(__name__)


def _notify_download_problem(url, report_file_id, agency_acronym, exc):
    """
    Send a diagnostic email when a report download fails.
    """
    subject = f"ReportDownloader failure for report_file {report_file_id}"
    message = (
        "An error occurred while downloading a report file.\n\n"
        f"URL: {url}\n"
        f"Report file ID: {report_file_id}\n"
        f"Agency acronym: {agency_acronym}\n"
        f"Exception: {exc.__class__.__name__}: {exc}\n\n"
        "Traceback:\n"
        f"{traceback.format_exc()}"
    )
    mail_admins(subject, message, fail_silently=True)


def _recheck_flag_for_report_file(report_file_id):
    try:
        report_file = ReportFile.objects.select_related('report').get(pk=report_file_id)
    except ReportFile.DoesNotExist:
        logger.warning("Cannot recheck flags: report_file %s does not exist.", report_file_id)
        return

    recheck_flag(report=report_file.report)


@task(name="download_file", autoretry_for=(requests.exceptions.ConnectionError, RetryHTTPError), retry_backoff=60)
def download_file(url, report_file_id, agency_acronym):
    downloader = ReportDownloader(
        url=url,
        report_file_id=report_file_id,
        agency_acronym=agency_acronym
    )
    try:
        downloader.download()
    except Exception as exc:
        _notify_download_problem(url, report_file_id, agency_acronym, exc)
        raise
    finally:
        try:
            _recheck_flag_for_report_file(report_file_id)
        except Exception:
            logger.exception("Failed to recheck flags for report_file %s.", report_file_id)


@task(name="send_submission_email")
def send_submission_email(response, institution_id_max, total_submission, agency_email, version='v2'):
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

    if version == 'v1':
        template_name = 'email/submission-v1.tpl'
    else:
        template_name = 'email/submission.tpl'

    message = EmailMessage(template_name, context=context,
                           from_email=from_email,
                           to=[agency_email],
                           cc=cc)
    message.send()


@task(name="recheck_flag")
def recheck_flag(report):
    report_flagger = ReportFlagger(report=report)
    report_flagger.check_and_set_flags()
