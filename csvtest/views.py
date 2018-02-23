import json

import datetime
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from submissionapi.csv_handler import CSVHandler
from submissionapi.flaggers.report_flagger import ReportFlagger
from submissionapi.models import SubmissionLog
from submissionapi.populators.populator import Populator
from submissionapi.serializers.response_serializers import ReportResponseSerializer
from submissionapi.serializers.submisson_serializers import SubmissionPackageSerializer
from submissionapi.tasks import send_submission_email


@login_required(login_url="/login")
def upload_csv(request, csv_file=None):
    response_list = []
    response_contains_error = False

    data = {}
    if "GET" == request.method:
        return render(request, "csvtest/upload_csv.html", data)

    # if not GET, then proceed
    try:
        csv_file = request.FILES["csv_file"]
        separator = request.POST.get("delimiter", ",")
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not CSV type')
            return HttpResponseRedirect(reverse("csvtest:upload_csv"))

        #if file is too large, return
        if csv_file.multiple_chunks():
            messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
            return HttpResponseRedirect(reverse("csvtest:upload_csv"))

    except Exception as e:
        messages.error(request, "Unable to upload file. " + repr(e))

    # CSV File manage
    csv_file.seek(0)
    csv_file = io.StringIO(csv_file.read().decode('utf-8'))

    csv_hanlder = CSVHandler(
        csvfile=csv_file,
        separator=separator
    )
    csv_hanlder.handle()

    for data in csv_hanlder.submission_data:
        serializer = SubmissionPackageSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            populator = Populator(data=serializer.validated_data)
            populator.populate()
            flagger = ReportFlagger(report=populator.report)
            flagger.check_and_set_flags()
            create_log_entry(request.data, populator, flagger)
            response_list.append(make_success_response(populator, flagger))
        else:
            response_list.append(make_error_response(serializer, original_data={}))
            response_contains_error = True

    if response_contains_error:
        return render(request, 'csvtest/upload_csv.html', context={'response_list': response_list})
    else:
        send_submission_email.delay(response_list, request.user.email)
        return render(request, 'csvtest/upload_csv.html', context={'response_list': response_list})


def make_success_response(populator, flagger):
    institution_warnings = populator.institution_flag_log
    report_warnings = flagger.flag_log

    if len(institution_warnings) > 0 or len(report_warnings) > 0:
        sanity_check_status = "warnings"
    else:
        sanity_check_status = "success"

    serializer = ReportResponseSerializer(flagger.report)

    return {
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


def create_log_entry(original_data, populator, flagger):
    SubmissionLog.objects.create(
        agency=populator.agency,
        report=flagger.report,
        submitted_data=json.dumps(original_data),
        report_status=flagger.report.flag,
        report_warnings=json.dumps(flagger.flag_log),
        institution_warnings=json.dumps(populator.institution_flag_log),
        submission_date=datetime.date.today()
    )