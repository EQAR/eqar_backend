import io
from bs4 import UnicodeDammit
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from ipware import get_client_ip

from institutions.models import Institution
from submissionapi.csv_functions.csv_handler import CSVHandler
from submissionapi.flaggers.report_flagger import ReportFlagger
from submissionapi.populators.populator import Populator
from submissionapi.serializers.response_serializers import ReportResponseSerializer
from submissionapi.serializers.submisson_serializers import SubmissionPackageSerializer
from submissionapi.tasks import send_submission_email
from submissionapi.trackers.submission_tracker import SubmissionTracker


@login_required(login_url="/login")
def upload_csv(request, csv_file=None):
    # Save the highest institution id
    try:
        max_inst = Institution.objects.latest('id').id
    except ObjectDoesNotExist:
        max_inst = 0

    submitted_reports = []
    accepted_reports = []
    response_contains_valid = False

    data = {}
    if "GET" == request.method:
        return render(request, "csvtest/upload_csv.html", data)

    # if not GET, then proceed
    try:
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not CSV type')
            return HttpResponseRedirect(reverse("csvtest:upload_csv"))

        #if file is too large, return
        if csv_file.multiple_chunks():
            messages.error(request, "Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
            return HttpResponseRedirect(reverse("csvtest:upload_csv"))

    except Exception as e:
        messages.error(request, "Unable to upload file. " + repr(e))
        return HttpResponseRedirect(reverse("csvtest:upload_csv"))

    # CSV File manage
    csv_file.seek(0)
    dammit = UnicodeDammit(csv_file.read())
    original_data = dammit.unicode_markup
    csv_object = io.StringIO(original_data)

    csv_handler = CSVHandler(csvfile=csv_object)
    csv_handler.handle()

    # Tracking
    client_ip, is_routable = get_client_ip(request)
    tracker = SubmissionTracker(original_data=original_data,
                                origin='csv',
                                user_profile=request.user.deqarprofile,
                                ip_address=client_ip)
    tracker.log_package()

    if csv_handler.error:
        messages.error(request, csv_handler.error_message)
        return HttpResponseRedirect(reverse("csvtest:upload_csv"))

    for data in csv_handler.submission_data:
        serializer = SubmissionPackageSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            populator = Populator(data=serializer.validated_data)
            populator.populate()
            flagger = ReportFlagger(report=populator.report)
            flagger.check_and_set_flags()
            tracker.log_report(populator, flagger)
            submitted_reports.append(make_success_response(populator, flagger))
            accepted_reports.append(make_success_response(populator, flagger))
            response_contains_valid = True
        else:
            submitted_reports.append(make_error_response(serializer, original_data={}))


    if response_contains_valid:
        send_submission_email.delay(response=accepted_reports,
                                    institution_id_max=max_inst,
                                    total_submission=len(submitted_reports),
                                    agency_email=request.user.email)
        return render(request, 'csvtest/upload_csv.html',
                      context={'response_list': submitted_reports})
    else:
        return render(request, 'csvtest/upload_csv.html',
                      context={'response_list': submitted_reports})


def make_success_response(populator, flagger):
    institution_warnings = populator.institution_flag_log
    report_warnings = flagger.flag_log

    if len(institution_warnings) > 0 or len(report_warnings) > 0:
        sanity_check_status = "warnings"
    else:
        sanity_check_status = "success"

    serializer = ReportResponseSerializer(flagger.report)

    return {
        'agency': populator.report.agency.deqar_id,
        'report': populator.report.id,
        'submission_status': 'success',
        'submitted_report': serializer.data,
        'sanity_check_status': sanity_check_status,
        'report_flag': flagger.report.flag.flag,
        'report_warnings': report_warnings,
        'institution_warnings': institution_warnings
    }


def make_error_response(serializer, original_data):
    return {
        'submission_status': 'errors',
        'original_data': original_data,
        'errors': serializer.errors
    }