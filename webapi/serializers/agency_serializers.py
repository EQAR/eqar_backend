from rest_framework import serializers
from agencies.models import *


class AgencyListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:agency-detail")
    primary_title = serializers.CharField(source='get_primary_name', read_only=True)
    primary_acronym = serializers.CharField(source='get_primary_acronym', read_only=True)

    class Meta:
        model = Agency
        fields = ['id', 'url', 'deqar_id', 'primary_title', 'primary_acronym', 'logo']


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


class AgencyESGActivitySerializer(serializers.ModelSerializer):
    activity_type = serializers.StringRelatedField()

    class Meta:
        model = AgencyESGActivity
        fields = ['activity', 'activity_description', 'activity_type', 'reports_link']


class AgencyEQARDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyEQARDecision
        fields = ['decision_date', 'decision_type__type', 'decision_file', 'decision_file_extra']


class AgencyHistoricalDataSerializer(serializers.ModelSerializer):
    field = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = AgencyHistoricalData
        fields = ['field', 'value', 'valid_from', 'valid_to']


class AgencyDetailSerializer(serializers.ModelSerializer):
    names = AgencyNameSerializer(many=True, read_only=True, source='agencyname_set')
    phone_numbers = serializers.StringRelatedField(many=True, source='agencyphone_set')
    emails = serializers.StringRelatedField(many=True, source='agencyemail_set')
    country = serializers.StringRelatedField()
    activities = AgencyESGActivitySerializer(many=True, read_only=True, source='agencyesgactivity_set')
    associations = serializers.StringRelatedField(many=True, read_only=True, source='agencymembership_set')
    decisions = AgencyEQARDecisionSerializer(many=True, read_only=True, source='agencydecision_set')
    historical_data = AgencyHistoricalDataSerializer(many=True, read_only=True, source='agencyhistoricaldata_set')
    geographical_focus = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Agency
        fields = ('id', 'deqar_id', 'names', 'contact_person', 'registration_start', 'registration_valid_to', 'registration_note',
                  'phone_numbers', 'address', 'country', 'emails', 'website_link', 'logo',
                  'activities', 'associations', 'decisions', 'specialisation_note',
                  'description_note', 'geographical_focus', 'historical_data',)

