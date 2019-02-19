from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from reports.models import Report, ReportFile


class ReportFileDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFile
        fields = ['file_display_name', 'file']


class ReportDashboardSerializer(serializers.ModelSerializer):
    agency = serializers.SlugRelatedField(read_only=True, slug_field='acronym_primary')
    institutions = serializers.StringRelatedField(many=True)
    programmes = serializers.StringRelatedField(many=True, source='programme_set')
    flag = serializers.StringRelatedField()
    date = serializers.SerializerMethodField()
    report_files = ReportFileDashboardSerializer(many=True, read_only=True, source='reportfile_set')

    class Meta:
        model = Report
        fields = ['id', 'agency', 'name', 'institutions', 'programmes', 'flag', 'date', 'report_files', 'flag_log']

    def get_date(self, obj):
        try:
            logs = obj.submissionreportlog_set.latest('submission_date')
            if logs:
                return logs.submission_date
            else:
                return None
        except ObjectDoesNotExist:
            return None
