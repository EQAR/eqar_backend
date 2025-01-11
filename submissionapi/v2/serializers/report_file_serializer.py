from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from adminapi.fields import PDFBase64File
from reports.models import ReportFile
from submissionapi.serializer_fields.report_identifier_field_with_integer import ReportIdentifierPlusIntegerField
from submissionapi.serializer_fields.report_language_field import ReportLanguageField


class ReportFileSerializer(serializers.Serializer):
    report_file_id = serializers.PrimaryKeyRelatedField(
        required=False, label='Identifier of the report-file record', queryset=ReportFile.objects.all()
    )
    original_location = serializers.URLField(max_length=500, required=False, label='The URL of the report file',
                                             help_text='example: "http://estudis.aqu.cat/MAD2014_UPC_es.pdf"')
    display_name = serializers.CharField(max_length=255, required=False, label='Display value of the file',
                                         help_text='example: "Ev. de la Solicitud de Verification de Título oficial"')
    report_language = serializers.ListField(child=ReportLanguageField(required=True), required=True,
                                            label='Language(s) of the report',
                                            help_text='example: ["eng", "ger"]')
    file = PDFBase64File(required=False, label='The report file in PDF format encoded with Base64')
    file_name = serializers.CharField(required=False, max_length=255, allow_blank=True,
                                      label='The name of the file, required if you embed the file in the upload request',
                                      help_text='example: ACQUIN_institutional_report.pdf')

    def validate(self, data):
        file = data.get('file', None)
        file_name = data.get('file_name', None)

        original_location = data.get('original_location', None)

        if file:
            if not file_name or file_name == '':
                raise ValidationError("Please provide a file name for the uploaded file.")

            if original_location:
                raise ValidationError("You cannot submit both a file and an original_location URL.")

        if not file and not original_location:
            raise ValidationError("Either file or original_location URL is required.")

        return super(ReportFileSerializer, self).validate(data)

    class Meta:
        ref_name = "ReportFileV2Serializer"


class ReportFileCreateSerializer(ReportFileSerializer):
    report_id = ReportIdentifierPlusIntegerField(required=True, label='DEQAR identifier of the report')

class ReportFileUpdateSerializer(ReportFileSerializer):
    report_file_id = serializers.PrimaryKeyRelatedField(
        required=True, label='Identifier of the report-file record', queryset=ReportFile.objects.all()
    )

class ReportFileDeleteSerializer(serializers.Serializer):
    report_file_id = serializers.PrimaryKeyRelatedField(
        required=True, label='Identifier of the report-file record', queryset=ReportFile.objects.all()
    )
