from django.db.models import Q

from rest_framework import serializers

from datedelta import datedelta
from rest_framework.utils.representation import manager_repr

from eqar_backend.serializer_fields.date_unix_timestamp import UnixTimestampDateField

from agencies.models import Agency
from countries.models import Country
from programmes.models import Programme, ProgrammeName
from reports.models import Report, ReportFile, ReportLink
from agencies.models import AgencyESGActivity
from institutions.models import Institution, InstitutionCountry


class AgencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Agency
        fields = [
            'id',
            'acronym_primary',
        ]

class EsgActivitySerializer(serializers.ModelSerializer):

    type = serializers.CharField(source='activity_type.type')
    group_id = serializers.PrimaryKeyRelatedField(source='activity_group', read_only=True, many=False)

    class Meta:
        model = AgencyESGActivity
        fields = [
            'id',
            'group_id',
            'type',
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

class ProgrammeNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProgrammeName
        fields = [ 'id', 'name', 'qualification', 'name_is_primary' ]

class ProgrammeSerializer(serializers.ModelSerializer):

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
                    'qf_ehea_level',
                    'nqf_level',
                    'workload_ects',
                    'degree_outcome',
                    'programme_type',
                    'assessment_certification',
                    'learning_outcomes',
                    'learning_outcome_description',
                    'field_study',
                ]

class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = [  'id',
                    'iso_3166_alpha2',
                    'iso_3166_alpha3',
                    'name_english',
                    'ehea_is_member',
                ]

class InstitutionCountrySerializer(serializers.ModelSerializer):

    country = CountrySerializer()
    country_valid_from = UnixTimestampDateField()
    country_valid_to = UnixTimestampDateField()

    class Meta:
        model = InstitutionCountry
        fields = [  'country',
                    'city',
                    'country_verified',
                    'country_valid_from',
                    'country_valid_to',
                ]

class InstitutionSerializer(serializers.ModelSerializer):

    locations = InstitutionCountrySerializer(many=True, read_only=True, source='institutioncountry_set')

    class Meta:
        model = Institution
        fields = [  'id',
                    'deqar_id',
                    'name_sort',
                    'name_primary',
                    'website_link',
                    'is_other_provider',
                    'locations',
                ]

class ReportIndexerSerializer(serializers.ModelSerializer):

    agency = AgencySerializer()
    contributing_agencies = AgencySerializer(read_only=True, many=True)
    agency_esg_activities = EsgActivitySerializer(read_only=True, many=True)
    institutions = InstitutionSerializer(read_only=True, many=True)
    platforms = InstitutionSerializer(read_only=True, many=True)
    programmes = ProgrammeSerializer(source='programme_set', read_only=True, many=True)
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
    other_provider_covered = serializers.SerializerMethodField()

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

    def get_other_provider_covered(self, obj):
        return any(obj.institutions.values_list('is_other_provider', flat=True))

    class Meta:
        model = Report
        fields = [
            'id',
            'local_identifier',
            'agency', 'contributing_agencies',
            'agency_esg_activities',
            'institutions',
            'platforms',
            'programmes',
            'decision', 'status',
            'valid_from', 'valid_to', 'valid_to_calculated',
            'created_at', 'updated_at',
            'crossborder',
            'report_files',
            'report_links',
            'other_provider_covered',
            'summary',
            'other_comment',
            'flag'
        ]


