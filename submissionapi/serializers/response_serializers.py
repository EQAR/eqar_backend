from rest_framework import serializers

from institutions.models import Institution
from programmes.models import Programme
from reports.models import Report, ReportFile


class InstitutionSerializer(serializers.ModelSerializer):
    eter_id = serializers.SlugRelatedField(slug_field='eter_id', read_only=True, source='eter')

    class Meta:
        model = Institution
        fields = ('id', 'deqar_id', 'eter_id', 'name_primary')


class ProgrammeSerializer(serializers.ModelSerializer):
    countries = serializers.StringRelatedField(many=True)

    class Meta:
        model = Programme
        fields = ('id', 'name_primary', 'countries')


class ReportFileSerializer(serializers.ModelSerializer):
    languages = serializers.StringRelatedField(many=True)

    class Meta:
        model = ReportFile
        fields = ('id', 'file_display_name', 'file_original_location', 'file', 'languages')


class ReportResponseSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField()
    agency_esg_activity = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    files = ReportFileSerializer(many=True, source='reportfile_set')
    institutions = InstitutionSerializer(many=True)
    programmes = ProgrammeSerializer(many=True, source='programme_set')

    class Meta:
        model = Report
        fields = ('id', 'agency', 'local_identifier', 'agency_esg_activity', 'name', 'status', 'decision',
                  'valid_from', 'valid_to', 'files', 'institutions', 'programmes')