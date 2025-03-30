from django.db.models import Q

from rest_framework import serializers

from datedelta import datedelta

from eqar_backend.serializer_fields.date_unix_timestamp import UnixTimestampDateField

from programmes.models import Programme
from reports.models import Report

from reports.serializers.report_meili_indexer_serializer import \
    AgencySerializer, \
    EsgActivitySerializer, \
    ReportFileSerializer, \
    ReportLinkSerializer, \
    ProgrammeNameSerializer


class ReportSerializer(serializers.ModelSerializer):

    agency = AgencySerializer()
    contributing_agencies = AgencySerializer(read_only=True, many=True)
    agency_esg_activities = EsgActivitySerializer(read_only=True, many=True)
    crossborder = serializers.SerializerMethodField()
    flag = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    valid_from = UnixTimestampDateField()
    valid_to = UnixTimestampDateField()
    valid_to_calculated = serializers.SerializerMethodField()
    created_at = UnixTimestampDateField()
    updated_at = UnixTimestampDateField()
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
            'agency_esg_activities',
            'decision', 'status',
            'valid_from', 'valid_to', 'valid_to_calculated',
            'created_at', 'updated_at',
            'crossborder',
            'report_files',
            'report_links',
            'summary',
            'other_comment',
            'flag'
        ]


class ProgrammeIndexerSerializer(serializers.ModelSerializer):

    report = ReportSerializer()
    institutions = serializers.PrimaryKeyRelatedField(source='report.institutions', read_only=True, many=True)
    platforms = serializers.PrimaryKeyRelatedField(source='report.platforms', read_only=True, many=True)
    names = ProgrammeNameSerializer(source='programmename_set', read_only=True, many=True)
    programme_type = serializers.SerializerMethodField()
    degree_outcome = serializers.PrimaryKeyRelatedField(read_only=True, many=False)
    qf_ehea_level = serializers.StringRelatedField()
    assessment_certification = serializers.StringRelatedField()
    learning_outcomes = serializers.SlugRelatedField(slug_field='learning_outcome_esco', many=True, read_only=True, source='programmelearningoutcome_set')

    def get_programme_type(self, obj):
        return obj.get_programme_type()

    class Meta:
        model = Programme
        fields = [  'id',
                    'names',
                    'name_primary',
                    'institutions',
                    'platforms',
                    'qf_ehea_level',
                    'nqf_level',
                    'workload_ects',
                    'degree_outcome',
                    'programme_type',
                    'assessment_certification',
                    'learning_outcomes',
                    'learning_outcome_description',
                    'field_study',
                    'report',
                ]

