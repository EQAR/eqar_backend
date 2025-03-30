from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from reports.models import Report
from submissionapi.v2.serializers.check_local_identifier_serializer import CheckLocalIdentifierSerializer
from submissionapi.v2.serializers.response_serializers import ResponseReportSerializer


class CheckLocalIdentifierView(APIView):
    """
        Check if the local identifier is resolving to an existing report.
    """
    @swagger_auto_schema(
        query_serializer=CheckLocalIdentifierSerializer,
        responses={
            '200': ResponseReportSerializer,
            '400': None,
            '404': None
        })
    def get(self, request):
        serializer = CheckLocalIdentifierSerializer(data=request.query_params)
        if serializer.is_valid():
            agency = serializer.validated_data['agency']
            local_identifier = serializer.validated_data['local_identifier']
            try:
                report = Report.objects.get(agency=agency, local_identifier=local_identifier)
                response_serializer = ResponseReportSerializer(report)
                return Response(response_serializer.data, status=HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response("Not Found", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)