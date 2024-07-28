from django.db.models import Q

from rest_framework import serializers

from eqar_backend.serializer_fields.date_unix_timestamp import UnixTimestampDateField

from programmes.models import Programme, ProgrammeName
from reports.models import Report
from agencies.models import AgencyESGActivity


class EsgActivitySerializer(serializers.ModelSerializer):

    type = serializers.CharField(source='activity_type.type')

    class Meta:
        model = AgencyESGActivity
        fields = [
            'id', 'type'
        ]

class ReportSerializer(serializers.ModelSerializer):

    agency = serializers.PrimaryKeyRelatedField(read_only=True, many=False)
    contributing_agencies = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    agency_esg_activity = EsgActivitySerializer()
    crossborder = serializers.SerializerMethodField()
    flag_level = serializers.CharField(source='flag.flag')
    status = serializers.CharField(source='status.status')
    decision = serializers.CharField(source='decision.decision')
    valid_from = UnixTimestampDateField()
    valid_to = UnixTimestampDateField()

    def get_crossborder(self, obj):
        crossborder = False
        focus_countries = obj.agency.agencyfocuscountry_set
        for inst in obj.institutions.all():
            for ic in inst.institutioncountry_set.filter(country_verified=True):
                if not focus_countries.filter(Q(country__id=ic.country.id) & Q(country_is_crossborder=False)):
                    crossborder = True
        return crossborder

    class Meta:
        model = Report
        fields = [
            'id',
            'agency', 'contributing_agencies',
            'agency_esg_activity',
            'decision', 'status',
            'valid_from', 'valid_to',
            'crossborder',
            'flag_level'
        ]


class ProgrammeNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProgrammeName
        fields = [ 'id', 'name', 'qualification', 'name_is_primary' ]

class ProgrammeIndexerSerializer(serializers.ModelSerializer):

    report = ReportSerializer()
    institutions = serializers.PrimaryKeyRelatedField(source='report.institutions', read_only=True, many=True)
    names = ProgrammeNameSerializer(source='programmename_set', read_only=True, many=True)
    name_primary = serializers.SerializerMethodField()
    programme_type = serializers.SerializerMethodField()
    degree_outcome = serializers.SlugRelatedField(slug_field='outcome', read_only=True)
    qf_ehea_level = serializers.SlugRelatedField(slug_field='level', read_only=True)

    def get_name_primary(self, obj):
        return obj.programmename_set.get(name_is_primary=True).name

    def get_programme_type(self, obj):
        return obj.get_programme_type()

    class Meta:
        model = Programme
        fields = [  'id',
                    'names',
                    'name_primary',
                    'institutions',
                    'qf_ehea_level',
                    'workload_ects',
                    'degree_outcome',
                    'programme_type',
                    'report',
                ]

