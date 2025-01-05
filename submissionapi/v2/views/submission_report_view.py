from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from adminapi.permissions import CanEditReport
from lists.models import Flag
from reports.models import Report, ReportFlag, ReportUpdateLog
from submissionapi.v2.serializers.response_serializers import ResponseReportSuccessResponseSerializer, \
    ResponseReportErrorResponseSerializer
from submissionapi.v2.serializers.submisson_serializers import SubmissionPackageCreateSerializer, \
    SubmissionPackageUpdateSerializer
from submissionapi.v2.submission_package_handler import SubmissionPackageHandler


class SubmissionReportView(APIView):
    """
        Submission of report data: POST request for creation, PUT request for update
    """
    @swagger_auto_schema(
        request_body=SubmissionPackageCreateSerializer,
        responses={
            '200': ResponseReportSuccessResponseSerializer,
            '201': None,
            '400': ResponseReportErrorResponseSerializer
        })
    def post(self, request):
        serializer = SubmissionPackageCreateSerializer(data=request.data, context={'request': request})
        handler = SubmissionPackageHandler(request=request, serializer=serializer, action='create')
        handler.handle()
        if handler.status == 'success':
            return Response(handler.response, status=status.HTTP_200_OK)
        else:
            return Response(handler.response, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=SubmissionPackageUpdateSerializer,
        responses={
            '200': ResponseReportSuccessResponseSerializer,
            '201': None,
            '400': ResponseReportErrorResponseSerializer
        })
    def put(self, request):
        serializer = SubmissionPackageUpdateSerializer(data=request.data, context={'request': request})
        handler = SubmissionPackageHandler(request=request, serializer=serializer, action='update')
        handler.handle()
        if handler.status == 'success':
            return Response(handler.response, status=status.HTTP_200_OK)
        else:
            return Response(handler.response, status=status.HTTP_400_BAD_REQUEST)

    '''
    def patch(self, request):
        serializer = SubmissionPackageUpdateSerializer(data=request.data, context={'request': request}, partial=True)
        handler = SubmissionPackageHandler(request=request, serializer=serializer, action='update')
        handler.handle()
        if handler.status == 'success':
            return Response(handler.response, status=status.HTTP_200_OK)
        else:
            return Response(handler.response, status=status.HTTP_400_BAD_REQUEST)
    '''

class ReportDelete(generics.DestroyAPIView):
    """
        Requests report records to be not visible on the public and on the search interface.
    """
    permission_classes = (CanEditReport|IsAdminUser,)

    @swagger_auto_schema(responses={'200': 'OK'})
    def delete(self, request, *args, **kwargs):
        report = get_object_or_404(Report, id=kwargs.get('pk'))
        flag = Flag.objects.get(flag='high level')
        report_flag, created = ReportFlag.objects.get_or_create(
            report=report,
            flag=flag,
            flag_message='Deletion was requested.',
        )
        if created or report_flag.active is False:
            ReportUpdateLog.objects.create(
                report=report,
                note='Deletion flag was assigned.',
                updated_by=request.user
            )
            report_flag.active = True
            report_flag.removed_by_eqar = False
            report_flag.save()
        return Response(data={'OK'}, status=200)