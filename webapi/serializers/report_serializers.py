from rest_framework import serializers
from reports.models import Report, ReportFile


class ReportFileSerializer(serializers.ModelSerializer):
    languages = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ReportFile
        fields = ['file_display_name', 'file', 'languages']


class ReportSerializer(serializers.ModelSerializer):
    agency_url = serializers.HyperlinkedRelatedField(read_only=True, view_name="webapi-v1:agency-detail",
                                                     source='agency')
    agency_name = serializers.StringRelatedField(source='agency')
    report_files = ReportFileSerializer(many=True, read_only=True, source='reportfile_set')
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    flag = serializers.StringRelatedField()

    class Meta:
        model = Report
        fields = ['agency_name', 'agency_url', 'valid_from', 'valid_to', 'status', 'decision', 'report_files',
                  'local_identifier', 'name', 'flag']
