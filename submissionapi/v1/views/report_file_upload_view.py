from django.core.exceptions import ObjectDoesNotExist
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from reports.models import ReportFile
from submissionapi.flaggers.report_flagger import ReportFlagger
from submissionapi.permissions import CanSubmitToAgency


class ReportFileUploadView(APIView):
    """
        Responsible for the submission of report files
    """
    parser_classes = (FileUploadParser,)
    permission_classes = (CanSubmitToAgency,)
    swagger_schema = None

    def put(self, request, filename, pk, format=None):
        file_obj = request.data['file']
        try:
            report_file = ReportFile.objects.get(pk=pk)
            report_file.file.delete(save=False)
            report_file.file.save(filename, file_obj, save=True)
            flagger = ReportFlagger(report=report_file.report)
            flagger.check_and_set_flags()
            return Response(status=204)
        except ObjectDoesNotExist:
            return Response(status=404)
