from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.models import ReportFile
from submissionapi.populators.report_file_populator import ReportFilePopulator
from submissionapi.v2.serializers.report_file_serializer import ReportFileCreateSerializer, ReportFileUpdateSerializer, \
    ReportFileDeleteSerializer


class ReportFileView(APIView):
    """
        Responsible for the update of report files
    """
    def post(self, request, *args, **kwargs):
        serializer = ReportFileCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            report_file_populator = ReportFilePopulator(
                report=serializer.validated_data['report_id'],
                report_file_data=serializer.validated_data,
                user=request.user
            )
            if report_file_populator.check_permission():
                report_file_populator.report_file_create()
                return Response('success', status=status.HTTP_200_OK)
            else:
                return Response({"error": "You don't have permission to add files to this report."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        serializer = ReportFileUpdateSerializer(data=request.data)
        if serializer.is_valid():
            report_file = serializer.validated_data['report_file_id']
            report_file_populator = ReportFilePopulator(
                report=report_file.report,
                report_file=report_file,
                report_file_data=serializer.validated_data,
                user=request.user
            )
            if report_file_populator.check_permission():
                report_file_populator.report_file_update()
                return Response('success', status=status.HTTP_200_OK)
            else:
                return Response({"error": "You don't have permission to add files to this report."},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        serializer = ReportFileDeleteSerializer(data=request.data)
        if serializer.is_valid():
            report_file = serializer.validated_data['report_file_id']

            report_file_populator = ReportFilePopulator(
                report=report_file.report,
                report_file=report_file,
                user=request.user
            )

            if report_file_populator.check_permission():
                file_count = ReportFile.objects.filter(report=report_file.report).count()
                if file_count == 1:
                    return Response(
                        {"error": "You can't delete the last file of a report. Please submit a new file first."},
                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    report_file.delete()
                return Response('deleted', status=status.HTTP_200_OK)
            else:
                return Response({"error": "You don't have permission to add files to this report."},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
