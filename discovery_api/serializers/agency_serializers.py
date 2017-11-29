from rest_framework import serializers
from agencies.models import *


class AgencyListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="discovery_api:agency-detail")
    primary_title = serializers.CharField(source='get_primary_name', read_only=True)
    primary_acronym = serializers.CharField(source='get_primary_acronym', read_only=True)

    class Meta:
        model = Agency
        fields = ['id', 'url', 'eqar_id', 'primary_title', 'primary_acronym']


class AgencyNameVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyNameVersion
        fields = ['name', 'name_transliterated', 'name_is_primary',
                  'acronym', 'acronym_transliterated', 'acronym_is_primary']


class AgencyNameSerializer(serializers.ModelSerializer):
    name_versions = AgencyNameVersionSerializer(many=True, read_only=True, source='agencynameversion_set')

    class Meta:
        model = AgencyName
        fields = ['name_versions', 'name_note', 'valid_to']


class AgencyFocusCountrySerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AgencyFocusCountry
        fields = ['country', 'focus_country_official']


class AgencyESGActivitySerializer(serializers.ModelSerializer):
    activity_type = serializers.StringRelatedField()

    class Meta:
        model = AgencyESGActivity
        fields = ['esg_activity', 'activity_description', 'activity_type']


class AgencyEQARRenewalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyEQARRenewal
        fields = ['renewal_date', 'review_report_file', 'decision_file']


class AgencyEQARChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyEQARChange
        fields = ['change_date', 'change_report_file']


class AgencyHistoricalDataSerializer(serializers.ModelSerializer):
    field = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = AgencyHistoricalData
        fields = ['field', 'value', 'valid_from', 'valid_to']


class AgencyDetailSerializer(serializers.ModelSerializer):
    names = AgencyNameSerializer(many=True, read_only=True, source='agencyname_set')
    phone_numbers = serializers.StringRelatedField(many=True, source='agencyphone_set')
    emails = serializers.StringRelatedField(many=True, source='agencyemail_set')
    locations = serializers.StringRelatedField(many=True, read_only=True, source='agencylocationcountry_set')
    focus_countries = AgencyFocusCountrySerializer(many=True, read_only=True, source='agencyfocuscountry_set')
    activities = AgencyESGActivitySerializer(many=True, read_only=True, source='agencyesgactivity_set')
    qf_ehea_levels = serializers.StringRelatedField(many=True, read_only=True, source='agencylevel_set')
    associations = serializers.StringRelatedField(many=True, read_only=True, source='agencymembership_set')
    renewals = AgencyEQARRenewalSerializer(many=True, read_only=True, source='agencyeqarrenewal_set')
    historical_data = AgencyHistoricalDataSerializer(many=True, read_only=True, source='agencyhistoricaldata_set')
    enqua_membership = serializers.StringRelatedField(read_only=True)
    focus = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Agency
        fields = ('names', 'registration_start', 'registration_valid_to', 'registration_note', 'phone_numbers',
                  'contact_person', 'address', 'emails', 'website_link', 'activity_note', 'locations',
                  'focus_countries', 'activities', 'qf_ehea_levels', 'associations', 'renewals', 'specialisation_note',
                  'activity_note', 'description_note', 'focus', 'enqua_membership', 'historical_data')

