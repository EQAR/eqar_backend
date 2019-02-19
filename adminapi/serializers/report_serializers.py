from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from adminapi.serializers.programme_serializers import ProgrammeSerializer
from adminapi.serializers.select_serializers import ReportStatusSerializer, ReportDecisionSerializer, \
    AgencySelectSerializer, AgencyESGActivitySerializer, LanguageSelectSerializer
from reports.models import Report, ReportFile
from adminapi.serializers.institution_serializers import InstitutionSerializer


class ReportFileSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='file_display_name')
    original_location = serializers.CharField(source='file_original_location')
    report_language = LanguageSelectSerializer(many=True, source='languages')

    class Meta:
        model = ReportFile
        fields = ('id', 'filename', 'original_location', 'file', 'report_language')


class ReportSerializer(WritableNestedModelSerializer):
    agency = AgencySelectSerializer()
    activity = AgencyESGActivitySerializer(source='agency_esg_activity')
    status = ReportStatusSerializer()
    decision = ReportDecisionSerializer()
    report_files = ReportFileSerializer(many=True, source='reportfile_set')
    institutions = InstitutionSerializer(many=True)
    programmes = ProgrammeSerializer(many=True, source='programme_set')

    class Meta:
        model = Report
        fields = ['id', 'agency', 'activity', 'local_identifier', 'name',
                  'status', 'decision',
                  'institutions', 'programmes', 'report_files',
                  'valid_from', 'valid_to']