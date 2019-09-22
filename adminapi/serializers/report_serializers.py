from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from adminapi.serializers.programme_serializers import ProgrammeWriteSerializer, ProgrammeReadSerializer
from adminapi.serializers.select_serializers import ReportStatusSerializer, ReportDecisionSerializer, \
    AgencySelectSerializer, AgencyESGActivitySerializer, LanguageSelectSerializer
from agencies.models import AgencyESGActivity
from lists.models import Language
from reports.models import Report, ReportFile, ReportFlag, ReportUpdateLog
from adminapi.serializers.institution_serializers import InstitutionReadSerializer


class ReportReadFileSerializer(WritableNestedModelSerializer):
    display_name = serializers.CharField(source='file_display_name')
    original_location = serializers.CharField(source='file_original_location')
    report_language = LanguageSelectSerializer(many=True, source='languages')
    filename = serializers.SerializerMethodField(source='file')
    filesize = serializers.SerializerMethodField(source='file')

    def get_filename(self, obj):
        if len(obj.file_original_location) == 0:
            return obj.file.name
        else:
            return ''

    def get_filesize(self, obj):
        try:
            return obj.file.size
        except Exception:
            return 0

    class Meta:
        model = ReportFile
        fields = ('id', 'display_name', 'original_location', 'file', 'filename', 'filesize', 'report_language')


class ReportWriteFileSerializer(WritableNestedModelSerializer):
    display_name = serializers.CharField(source='file_display_name', required=False, allow_blank=True)
    original_location = serializers.CharField(source='file_original_location', required=False, allow_blank=True)
    report_language = serializers.PrimaryKeyRelatedField(many=True, queryset=Language.objects.all(), source='languages')

    class Meta:
        model = ReportFile
        fields = ('id', 'display_name', 'original_location', 'report_language')


class ReportFlagSerializer(serializers.ModelSerializer):
    flag = serializers.StringRelatedField()

    class Meta:
        model = ReportFlag
        fields = ('id', 'flag', 'flag_message', 'active', 'removed_by_eqar')


class ReportUpdateLogSerializer(serializers.ModelSerializer):
    updated_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = ReportUpdateLog
        fields = ('id', 'note', 'updated_by', 'updated_at')


class ReportReadSerializer(serializers.ModelSerializer):
    agency = AgencySelectSerializer()
    activity = AgencyESGActivitySerializer(source='agency_esg_activity')
    status = ReportStatusSerializer()
    decision = ReportDecisionSerializer()
    report_files = ReportReadFileSerializer(many=True, source='reportfile_set', read_only=True)
    institutions = InstitutionReadSerializer(many=True)
    programmes = ProgrammeReadSerializer(many=True, source='programme_set')
    flags = ReportFlagSerializer(many=True, source='reportflag_set')
    update_log = ReportUpdateLogSerializer(many=True, source='reportupdatelog_set')
    created_by = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Report
        fields = ['id', 'agency', 'activity', 'local_identifier', 'name',
                  'status', 'decision',
                  'institutions', 'programmes', 'report_files',
                  'valid_from', 'valid_to', 'flags',
                  'created_at', 'updated_at', 'created_by', 'update_log',
                  'other_comment', 'internal_note']


class ReportWriteSerializer(WritableNestedModelSerializer):
    activity = serializers.PrimaryKeyRelatedField(queryset=AgencyESGActivity.objects.all(), source='agency_esg_activity')
    report_files = ReportWriteFileSerializer(many=True, source='reportfile_set')
    programmes = ProgrammeWriteSerializer(many=True, source='programme_set', required=False)

    class Meta:
        model = Report
        fields = ['id', 'agency', 'activity', 'local_identifier',
                  'status', 'decision',
                  'institutions', 'programmes', 'report_files',
                  'valid_from', 'valid_to', 'other_comment', 'internal_note']