from rest_framework import serializers
from reports.models import ReportFile, ReportLink


class ReportLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportLink
        fields = ['link_display_name', 'link']


class ReportFileSerializer(serializers.ModelSerializer):
    languages = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ReportFile
        fields = ['id', 'file_display_name', 'file', 'languages']
