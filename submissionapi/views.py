import json

import datetime

import os
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.models import ReportFile
from submissionapi.flaggers.report_flagger import ReportFlagger
from submissionapi.models import SubmissionLog
from submissionapi.permissions import CanSubmitToAgency
from submissionapi.populators.populator import Populator
from submissionapi.serializers.response_serializers import ReportResponseSerializer
from submissionapi.serializers.submisson_serializers import SubmissionPackageSerializer
from submissionapi.tasks import send_submission_email


class Submission(APIView):
    def post(self, request, format=None):
        # Check if request is a list:
        if isinstance(request.data, list):
            response_list = []
            response_contains_error = False

            for data in request.data:
                serializer = SubmissionPackageSerializer(data=data, context={'request': request})
                if serializer.is_valid():
                    populator = Populator(data=serializer.validated_data)
                    populator.populate()
                    flagger = ReportFlagger(report=populator.report)
                    flagger.check_and_set_flags()
                    self.create_log_entry(request.data, populator, flagger)
                    response_list.append(self.make_success_response(populator, flagger))
                else:
                    response_contains_error = True
                    response_list.append(self.make_error_response(serializer, data))

            if response_contains_error:
                return Response(response_list, status=status.HTTP_400_BAD_REQUEST)
            else:
                send_submission_email.delay(response_list, request.user.email)
                return Response(response_list, status=status.HTTP_200_OK)

        # If request is not a list
        else:
            serializer = SubmissionPackageSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                populator = Populator(data=serializer.validated_data)
                populator.populate()
                flagger = ReportFlagger(report=populator.report)
                flagger.check_and_set_flags()
                self.create_log_entry(request.data, populator, flagger)
                send_submission_email.delay([self.make_success_response(populator, flagger)], request.user.email)
                return Response(self.make_success_response(populator, flagger), status=status.HTTP_200_OK)
            else:
                return Response(self.make_error_response(serializer, request.data), status=status.HTTP_400_BAD_REQUEST)

    def make_success_response(self, populator, flagger):
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

    def make_error_response(self, serializer, original_data):
        return {
            'submission_status': 'errors',
            'original_data': original_data,
            'errors': serializer.errors
        }

    def create_log_entry(self, original_data, populator, flagger):
        SubmissionLog.objects.create(
            agency=populator.agency,
            report=flagger.report,
            submitted_data=json.dumps(original_data),
            report_status=flagger.report.flag,
            report_warnings=json.dumps(flagger.flag_log),
            institution_warnings=json.dumps(populator.institution_flag_log),
            submission_date=datetime.date.today()
        )


class ReportFileUploadView(APIView):
    parser_classes = (FileUploadParser,)
    permission_classes = (CanSubmitToAgency,)

    def put(self, request, filename, pk, format=None):
        file_obj = request.data['file']
        filename = "%s_%s" % ((datetime.datetime.now().strftime("%Y%m%d_%H%M")), filename)
        try:
            report_file = ReportFile.objects.get(pk=pk)
            agency_acronym = report_file.report.agency.acronym_primary
            file_path = os.path.join(settings.MEDIA_ROOT, agency_acronym, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

            report_file.file.name = os.path.join(agency_acronym, filename)
            report_file.save()
            return Response(status=204)
        except ObjectDoesNotExist:
            return Response(status=404)
