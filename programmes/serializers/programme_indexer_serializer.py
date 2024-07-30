from django.db.models import Q

from rest_framework import serializers

from datedelta import datedelta

from eqar_backend.serializer_fields.date_unix_timestamp import UnixTimestampDateField

from programmes.models import Programme, ProgrammeName
from reports.models import Report, ReportFile, ReportLink
from agencies.models import AgencyESGActivity


class EsgActivitySerializer(serializers.ModelSerializer):

    type = serializers.CharField(source='activity_type.type')

    class Meta:
        model = AgencyESGActivity
        fields = [
            'id', 'type'
        ]

class ReportFileSerializer(serializers.ModelSerializer):

    languages = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ReportFile
        fields = [
            'file_display_name',
            'file',
            'languages',
        ]

class ReportLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportLink
        fields = [
            'link_display_name',
            'link',
        ]

class ReportSerializer(serializers.ModelSerializer):

    agency = serializers.PrimaryKeyRelatedField(read_only=True, many=False)
    contributing_agencies = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    agency_esg_activity = EsgActivitySerializer()
    crossborder = serializers.SerializerMethodField()
    flag_level = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    valid_from = UnixTimestampDateField()
    valid_to = UnixTimestampDateField()
    valid_to_calculated = serializers.SerializerMethodField()
    report_files = ReportFileSerializer(source='reportfile_set', read_only=True, many=True)
    report_links = ReportLinkSerializer(source='reportlink_set', read_only=True, many=True)

    def get_crossborder(self, obj):
        crossborder = False
        focus_countries = obj.agency.agencyfocuscountry_set
        for inst in obj.institutions.all():
            for ic in inst.institutioncountry_set.filter(country_verified=True):
                if not focus_countries.filter(Q(country__id=ic.country.id) & Q(country_is_crossborder=False)):
                    crossborder = True
        return crossborder

    def get_valid_to_calculated(self, obj):
        field = UnixTimestampDateField()
        if obj.valid_to:
            return field.to_representation(obj.valid_to)
        else:
            return field.to_representation(obj.valid_from + datedelta(years=6))

    class Meta:
        model = Report
        fields = [
            'id',
            'local_identifier',
            'agency', 'contributing_agencies',
            'agency_esg_activity',
            'decision', 'status',
            'valid_from', 'valid_to', 'valid_to_calculated',
            'crossborder',
            'report_files',
            'report_links',
            'summary',
            'other_comment',
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
    degree_outcome = serializers.StringRelatedField()
    qf_ehea_level = serializers.StringRelatedField()
    assessment_certification = serializers.StringRelatedField()
    learning_outcomes = serializers.SlugRelatedField(slug_field='learning_outcome_esco', many=True, read_only=True, source='programmelearningoutcome_set')

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
                    'assessment_certification',
                    'learning_outcomes',
                    'learning_outcome_description',
                    'field_study',
                    'report',
                ]

