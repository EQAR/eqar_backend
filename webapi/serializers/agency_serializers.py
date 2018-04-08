from rest_framework import serializers
from agencies.models import *
from eqar_backend.serializers import HistoryFilteredListSerializer
from webapi.serializers.country_serializers import CountryListSerializer


class AgencyListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:agency-detail")
    name_primary = serializers.CharField(source='get_primary_name', read_only=True)
    acronym_primary = serializers.CharField(source='get_primary_acronym', read_only=True)
    country = CountryListSerializer()

    class Meta:
        model = Agency
        fields = ['id', 'url', 'deqar_id', 'name_primary', 'acronym_primary', 'logo', 'country']


class AgencyFocusCountrySerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField()
    country_url = serializers.HyperlinkedRelatedField(view_name="webapi-v1:country-detail", read_only=True,
                                                      source='country')

    class Meta:
        model = AgencyFocusCountry
        fields = ['country_url', 'country', 'country_is_official', 'country_is_crossborder', 'country_valid_from',
                  'country_valid_to']


class AgencyNameVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyNameVersion
        fields = ['name', 'name_transliterated', 'name_is_primary',
                  'acronym', 'acronym_transliterated', 'acronym_is_primary']


class AgencyNameSerializer(serializers.ModelSerializer):
    name_versions = AgencyNameVersionSerializer(many=True, read_only=True, source='agencynameversion_set')

    class Meta:
        model = AgencyName
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['id', 'name_versions', 'name_note', 'name_valid_to']


class AgencyESGActivitySerializer(serializers.ModelSerializer):
    activity_type = serializers.StringRelatedField()

    class Meta:
        model = AgencyESGActivity
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['id', 'activity', 'activity_description', 'activity_type', 'reports_link', 'activity_valid_to']


class AgencyEQARDecisionSerializer(serializers.ModelSerializer):
    decision_type = serializers.StringRelatedField()

    class Meta:
        model = AgencyEQARDecision
        fields = ['decision_date', 'decision_type', 'decision_file', 'decision_file_extra']


class AgencyHistoricalDataSerializer(serializers.ModelSerializer):
    field = serializers.StringRelatedField()

    class Meta:
        model = AgencyHistoricalData
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['field', 'record_id', 'value', 'valid_from', 'valid_to']


class AgencyDetailSerializer(serializers.ModelSerializer):
    names = AgencyNameSerializer(many=True, read_only=True, source='agencyname_set')
    phone_numbers = serializers.StringRelatedField(many=True, source='agencyphone_set')
    emails = serializers.StringRelatedField(many=True, source='agencyemail_set')
    country = serializers.StringRelatedField()
    activities = AgencyESGActivitySerializer(many=True, read_only=True, source='agencyesgactivity_set')
    associations = serializers.StringRelatedField(many=True, read_only=True, source='agencymembership_set')
    decisions = serializers.SerializerMethodField()
    historical_data = AgencyHistoricalDataSerializer(many=True, read_only=True, source='agencyhistoricaldata_set')
    geographical_focus = serializers.StringRelatedField(read_only=True)
    report_count = serializers.SerializerMethodField()

    def get_decisions(self, obj):
        queryset = AgencyEQARDecision.objects.filter(agency=self.instance).order_by('-decision_date')
        return AgencyEQARDecisionSerializer(queryset, many=True, context=self.context).data

    def get_report_count(self, obj):
        return obj.report_set.count()

    class Meta:
        model = Agency
        fields = ('id', 'deqar_id', 'names', 'contact_person', 'registration_start', 'registration_valid_to', 'registration_note',
                  'phone_numbers', 'address', 'country', 'emails', 'website_link', 'logo',
                  'report_count', 'activities', 'associations', 'decisions', 'specialisation_note',
                  'description_note', 'geographical_focus', 'historical_data',)

