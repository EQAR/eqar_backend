from rest_framework import serializers
from programmes.models import Programme, ProgrammeName, ProgrammeIdentifier
from webapi.serializers.report_detail_serializers import ReportDetailSerializer


class ProgrammeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammeName
        fields = ['name', 'name_is_primary', 'qualification']


class ProgrammeIdentifierSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField()

    class Meta:
        model = ProgrammeIdentifier
        fields = ['identifier', 'agency', 'resource']


class ProgrammeSerializer(serializers.ModelSerializer):
    programme_names = ProgrammeNameSerializer(many=True, read_only=True, source='programmename_set')
    programme_identifiers = ProgrammeIdentifierSerializer(many=True, read_only=True, source='programmeidentifier_set')
    countries = serializers.StringRelatedField(many=True, read_only=True)
    report = serializers.SerializerMethodField()
    qf_ehea_level = serializers.StringRelatedField(read_only=True)

    def get_report(self, obj):
        report = obj.report
        self.context['programme_name'] = obj.name_primary
        self.context['report_type'] = 'programme'
        self.context['qf_ehea_level'] = obj.qf_ehea_level.level if obj.qf_ehea_level else None
        serializer = ReportDetailSerializer(report, context=self.context)
        return serializer.data

    class Meta:
        model = Programme
        ref_name = 'ProgrammeSerializer_v2'
        fields = ['report', 'programme_names', 'programme_identifiers', 'nqf_level', 'qf_ehea_level', 'countries']
