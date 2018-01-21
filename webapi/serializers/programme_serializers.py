from rest_framework import serializers
from programmes.models import Programme, ProgrammeName
from webapi.serializers.report_serializers import ReportSerializer


class ProgrammeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammeName
        fields = ['name', 'name_is_primary', 'qualification']


class ProgrammeIdentifierSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField()

    class Meta:
        model = ProgrammeName
        fields = ['identifier', 'agency', 'resource']


class ProgrammeSerializer(serializers.ModelSerializer):
    programme_names = ProgrammeNameSerializer(many=True, read_only=True, source='programmename_set')
    programme_identifiers = ProgrammeIdentifierSerializer(many=True, read_only=True, source='programmeidentifier_set')
    countries = serializers.StringRelatedField(many=True, read_only=True)
    report = ReportSerializer()

    class Meta:
        model = Programme
        fields = ['report', 'programme_names', 'programme_identifiers', 'nqf_level', 'qf_ehea_level', 'countries']