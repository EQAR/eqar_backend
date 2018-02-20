import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from submissionapi.flaggers.report_flagger import ReportFlagger
from submissionapi.populators.populator import Populator
from submissionapi.serializers.response_serializers import ReportResponseSerializer
from submissionapi.serializers.submisson_serializers import SubmissionPackageSerializer


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
                    response_list.append(self.make_success_response(populator, flagger))
                else:
                    response_contains_error = True
                    response_list.append(self.make_error_response(serializer, data))

            if response_contains_error:
                return Response(response_list, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(response_list, status=status.HTTP_200_OK)

        # If request is not a list
        else:
            serializer = SubmissionPackageSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                populator = Populator(data=serializer.validated_data)
                populator.populate()
                flagger = ReportFlagger(report=populator.report)
                flagger.check_and_set_flags()
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