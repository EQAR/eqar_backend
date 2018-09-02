import datetime

import os
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from reports.models import ReportFile
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
