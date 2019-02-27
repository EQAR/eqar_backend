from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from adminapi.serializers.programme_serializers import ProgrammeSerializer
from adminapi.serializers.select_serializers import ReportStatusSerializer, ReportDecisionSerializer, \
    AgencySelectSerializer, AgencyESGActivitySerializer, LanguageSelectSerializer
from reports.models import Report, ReportFile, ReportFlag
from adminapi.serializers.institution_serializers import InstitutionSerializer


class ReportReadFileSerializer(WritableNestedModelSerializer):
    display_name = serializers.CharField(source='file_display_name')
    original_location = serializers.CharField(source='file_original_location')
    report_language = LanguageSelectSerializer(many=True, source='languages')

    class Meta:
        model = ReportFile
        fields = ('id', 'display_name', 'original_location', 'file', 'report_language')


class ReportWriteFileSerializer(WritableNestedModelSerializer):
    display_name = serializers.CharField(source='file_display_name', required=False, allow_blank=True)
    original_location = serializers.CharField(source='file_original_location', required=False, allow_blank=True)
    report_language = LanguageSelectSerializer(many=True, source='languages')

    class Meta:
        model = ReportFile
        fields = ('id', 'display_name', 'original_location', 'report_language')


class ReportFlagSerializer(serializers.ModelSerializer):
    flag = serializers.StringRelatedField()

    class Meta:
        model = ReportFlag
        fields = ('id', 'flag', 'flag_message', 'active', 'removed_by_eqar')


class ReportReadSerializer(serializers.ModelSerializer):
    agency = AgencySelectSerializer()
    activity = AgencyESGActivitySerializer(source='agency_esg_activity')
    status = ReportStatusSerializer()
    decision = ReportDecisionSerializer()
    report_files = ReportReadFileSerializer(many=True, source='reportfile_set', read_only=True)
    institutions = InstitutionSerializer(many=True)
    programmes = ProgrammeSerializer(many=True, source='programme_set')
    flags = ReportFlagSerializer(many=True, source='reportflag_set')

    class Meta:
        model = Report
        fields = ['id', 'agency', 'activity', 'local_identifier', 'name',
                  'status', 'decision',
                  'institutions', 'programmes', 'report_files',
                  'valid_from', 'valid_to', 'flags',
                  'created_at', 'updated_at']


class ReportWriteSerializer(WritableNestedModelSerializer):
    agency = AgencySelectSerializer()
    activity = AgencyESGActivitySerializer(source='agency_esg_activity')
    status = ReportStatusSerializer()
    decision = ReportDecisionSerializer()
    report_files = ReportWriteFileSerializer(many=True, source='reportfile_set')
    programmes = ProgrammeSerializer(many=True, source='programme_set')

    class Meta:
        model = Report
        fields = ['id', 'agency', 'activity', 'local_identifier', 'name',
                  'status', 'decision',
                  'institutions', 'programmes', 'report_files',
                  'valid_from', 'valid_to']