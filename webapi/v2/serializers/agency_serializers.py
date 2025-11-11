from django.db.models import Q
from rest_framework import serializers
from agencies.models import *
from institutions.models import Institution
from reports.models import Report
from webapi.v2.serializers.country_serializers import CountryListSerializer


class EsgActivitySerializer(serializers.ModelSerializer):
    group_id = serializers.PrimaryKeyRelatedField(source='activity_group', read_only=True)
    activity = serializers.CharField(source='activity_group.activity')
    activity_type = serializers.CharField(source='activity_group.activity_type.type')

    class Meta:
        model = AgencyESGActivity
        fields = [
            'id',
            'group_id',
            'activity',
            'activity_description',
            'reports_link',
            'activity_type',
            'activity_valid_to',
        ]


class EsgActivityDetailSerializer(EsgActivitySerializer):
    report_count = serializers.SerializerMethodField()
    institution_count = serializers.SerializerMethodField()

    def get_report_count(self, obj):
        return obj.reports.count()

    def get_institution_count(self, obj):
        return Institution.objects.filter(reports__agency_esg_activities=obj).distinct().count()

    class Meta:
        model = AgencyESGActivity
        fields = [
            'id',
            'group_id',
            'activity',
            'activity_description',
            'reports_link',
            'activity_type',
            'activity_valid_to',
            'report_count',
            'institution_count',
        ]


class AgencyListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v2:agency-detail")
    name_primary = serializers.CharField(source='get_primary_name', read_only=True)
    acronym_primary = serializers.CharField(source='get_primary_acronym', read_only=True)
    country = CountryListSerializer()
    activities = EsgActivitySerializer(many=True, read_only=True, source='agencyesgactivity_set')
    institution_count = serializers.SerializerMethodField()
    report_count = serializers.SerializerMethodField()

    def get_institution_count(self, obj):
        return Institution.objects.filter(Q(reports__agency=obj) | Q(reports__contributing_agencies=obj)).distinct().count()

    def get_report_count(self, obj):
        return Report.objects.filter(Q(agency=obj) | Q(contributing_agencies=obj)).count()

    class Meta:
        model = Agency
        fields = ['id', 'url', 'deqar_id', 'name_primary', 'acronym_primary', 'logo', 'country', 'activities',
                  'registration_start', 'registration_valid_to', 'registration_note',
                  'institution_count', 'report_count']


class AgencyListByFocusCountrySerializer(AgencyListSerializer):
    country_is_official = serializers.SerializerMethodField()
    report_count = serializers.SerializerMethodField()
    institution_count = serializers.SerializerMethodField()

    def get_report_count(self, obj):
        return Report.objects.filter(
                ( Q(agency=obj) | Q(contributing_agencies=obj) ) &
                Q(institutions__institutioncountry__country_id=self.context['country_id'])
            ).count()

    def get_institution_count(self, obj):
        return Institution.objects.filter(
                ( Q(reports__agency=obj) | Q(reports__contributing_agencies=obj) ) &
                Q(institutioncountry__country_id=self.context['country_id'])
            ).distinct().count()

    def get_country_is_official(self, obj):
        focus_country = obj.agencyfocuscountry_set.filter(country_id=self.context['country_id']).first()
        return focus_country.country_is_official

    class Meta:
        model = Agency
        fields = ['id', 'url', 'deqar_id', 'name_primary', 'acronym_primary', 'logo', 'country', 'activities',
                  'country_is_official', 'report_count', 'institution_count',
                  'is_registered', 'registration_start', 'registration_valid_to']


class AgencyFocusCountrySerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField()
    country_url = serializers.HyperlinkedRelatedField(view_name="webapi-v2:country-detail", read_only=True,
                                                      source='country')
    institution_count = serializers.SerializerMethodField()
    report_count = serializers.SerializerMethodField()
    country_is_ehea = serializers.SerializerMethodField()

    def get_institution_count(self, obj):
        return Institution.objects.filter(
            Q(institutioncountry__country=obj.country) &
            ( Q(reports__agency=obj.agency) | Q(reports__contributing_agencies=obj.agency) )
        ).distinct().count()

    def get_report_count(self, obj):
        return Report.objects.filter(
            Q(institutions__institutioncountry__country=obj.country) &
            ( Q(agency=obj.agency) | Q(contributing_agencies=obj.agency) )
        ).count()

    def get_country_is_ehea(self, obj):
        return obj.country.ehea_is_member

    class Meta:
        model = AgencyFocusCountry
        fields = ['country_url', 'country', 'country_is_official', 'country_is_crossborder', 'country_valid_from',
                  'country_valid_to', 'institution_count', 'report_count', 'country_is_ehea']


class AgencyNameVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyNameVersion
        fields = ['name', 'name_transliterated', 'name_is_primary',
                  'acronym', 'acronym_transliterated', 'acronym_is_primary']


class AgencyNameSerializer(serializers.ModelSerializer):
    name_versions = AgencyNameVersionSerializer(many=True, read_only=True, source='agencynameversion_set')

    class Meta:
        model = AgencyName
        fields = ['id', 'name_versions', 'name_note', 'name_valid_to']


class AgencyEQARDecisionSerializer(serializers.ModelSerializer):
    decision_type = serializers.StringRelatedField()

    class Meta:
        model = AgencyEQARDecision
        fields = ['decision_date', 'decision_type', 'decision_file', 'decision_file_extra']


class AgencyHistoricalDataSerializer(serializers.ModelSerializer):
    field = serializers.StringRelatedField()

    class Meta:
        model = AgencyHistoricalData
        fields = ['field', 'record_id', 'value', 'valid_from', 'valid_to']


class AgencyDetailSerializer(serializers.ModelSerializer):
    names = AgencyNameSerializer(many=True, read_only=True, source='agencyname_set')
    phone_numbers = serializers.StringRelatedField(many=True, source='agencyphone_set')
    emails = serializers.StringRelatedField(many=True, source='agencyemail_set')
    country = CountryListSerializer()
    activities = EsgActivityDetailSerializer(many=True, read_only=True, source='agencyesgactivity_set')
    associations = serializers.StringRelatedField(many=True, read_only=True, source='agencymembership_set')
    decisions = serializers.SerializerMethodField()
    historical_data = AgencyHistoricalDataSerializer(many=True, read_only=True, source='agencyhistoricaldata_set')
    geographical_focus = serializers.StringRelatedField(read_only=True)
    report_count = serializers.SerializerMethodField()
    institution_count = serializers.SerializerMethodField()

    def get_decisions(self, obj):
        queryset = AgencyEQARDecision.objects.filter(agency=self.instance).order_by('-decision_date')
        return AgencyEQARDecisionSerializer(queryset, many=True, context=self.context).data

    def get_report_count(self, obj):
        return obj.report_set.count() + obj.co_authored_reports.count()

    def get_institution_count(self, obj):
        return Institution.objects.filter(Q(reports__agency=obj) | Q(reports__contributing_agencies=obj)).distinct().count()

    class Meta:
        model = Agency
        fields = ('id', 'deqar_id', 'names', 'contact_person', 'is_registered', 'registration_start',
                  'registration_valid_to', 'registration_note', 'reports_link',
                  'phone_numbers', 'address', 'country', 'emails', 'website_link', 'logo',
                  'report_count', 'institution_count', 'activities', 'associations', 'decisions', 'specialisation_note',
                  'description_note', 'geographical_focus', 'historical_data',)


class AgencyEQARDecisionListSerializer(serializers.ModelSerializer):
    agency_acronym = serializers.SerializerMethodField()
    decision_type = serializers.StringRelatedField()

    def get_agency_acronym(self, obj):
        return obj.agency.acronym_primary

    class Meta:
        model = AgencyEQARDecision
        fields = ('agency_acronym', 'decision_date', 'decision_type', 'decision_file', 'decision_file_extra')


class AgencyActivityDEQARConnectListSerializer(serializers.ModelSerializer):
    agency = serializers.SlugRelatedField(read_only=True, slug_field='acronym_primary')
    group_id = serializers.PrimaryKeyRelatedField(source='activity_group', read_only=True)
    activity = serializers.CharField(source='activity_group.activity')
    activity_type = serializers.CharField(source='activity_group.activity_type.type')

    class Meta:
        model = AgencyESGActivity
        fields = ['id', 'group_id', 'agency', 'activity', 'activity_type', 'activity_description']


class AgencyActivityGroupMemberSerializer(serializers.ModelSerializer):
    agency = serializers.SlugRelatedField(read_only=True, slug_field='acronym_primary')

    class Meta:
        model = AgencyESGActivity
        fields = ['id', 'agency', 'activity_description', 'reports_link', 'activity_valid_from', 'activity_valid_to',]


class AgencyActivityGroupListSerializer(serializers.ModelSerializer):
    activity_type = serializers.StringRelatedField()
    members = AgencyActivityGroupMemberSerializer(many=True, read_only=True, source='agencyesgactivity_set')

    class Meta:
        model = AgencyActivityGroup
        fields = ['id', 'activity', 'activity_type', 'reports_link', 'members' ]


class ContributingAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ['id', 'name_primary', 'acronym_primary']
