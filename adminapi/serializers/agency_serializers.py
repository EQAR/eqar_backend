from rest_framework import serializers

from adminapi.serializers.select_serializers import CountrySelectSerializer, \
    AgencyActivityTypeSerializer, AssociationSelectSerializer, EQARDecisionTypeSelectSerializer
from agencies.models import Agency, AgencyName, AgencyNameVersion, AgencyPhone, AgencyEmail, AgencyFocusCountry, \
    AgencyESGActivity, AgencyMembership, AgencyEQARDecision, AgencyFlag, AgencyUpdateLog


class AgencyListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:agency-detail")
    name_primary = serializers.CharField(source='get_primary_name', read_only=True)
    acronym_primary = serializers.CharField(source='get_primary_acronym', read_only=True)
    country = serializers.SlugRelatedField(slug_field='name_english', read_only=True)

    class Meta:
        model = Agency
        fields = ['id', 'url', 'deqar_id', 'name_primary', 'acronym_primary', 'country',
                  'registration_start', 'registration_valid_to', 'registration_note']


class AgencyNameVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyNameVersion
        fields = '__all__'


class AgencyNameSerializer(serializers.ModelSerializer):
    agency_name_versions = AgencyNameVersionSerializer(many=True, source='agencynameversion_set')

    class Meta:
        model = AgencyName
        fields = '__all__'


class AgencyPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyPhone
        fields = '__all__'


class AgencyEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyEmail
        fields = '__all__'


class AgencyFocusCountrySerializer(serializers.ModelSerializer):
    country = CountrySelectSerializer()

    class Meta:
        model = AgencyFocusCountry
        fields = '__all__'


class AgencyESGActivityReadSerializer(serializers.ModelSerializer):
    activity_type = AgencyActivityTypeSerializer()

    class Meta:
        model = AgencyESGActivity
        fields = '__all__'


class AgencyMembershipSerializer(serializers.ModelSerializer):
    association = AssociationSelectSerializer()

    class Meta:
        model = AgencyMembership
        fields = '__all__'


class AgencyEQARDecisionSerializer(serializers.ModelSerializer):
    decision_type = EQARDecisionTypeSelectSerializer()
    decision_file_name = serializers.SerializerMethodField(source='decision_files')

    def get_decision_file_name(self, obj):
        return obj.decision_file.name.replace('EQAR/', '')

    class Meta:
        model = AgencyEQARDecision
        fields = '__all__'


class AgencyFlagSerializer(serializers.ModelSerializer):
    flag = serializers.StringRelatedField()

    class Meta:
        model = AgencyFlag
        fields = ('id', 'flag', 'flag_message', 'active', 'removed_by_eqar')


class AgencyUpdateLogSerializer(serializers.ModelSerializer):
    updated_by = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = AgencyUpdateLog
        fields = ('id', 'note', 'updated_at', 'updated_by')


class AgencyReadSerializer(serializers.ModelSerializer):
    primary_name_acronym = serializers.SerializerMethodField()
    names = AgencyNameSerializer(many=True, source='agencyname_set')
    phone_numbers = AgencyPhoneSerializer(many=True, source='agencyphone_set')
    emails = AgencyEmailSerializer(many=True, source='agencyemail_set')
    focus_countries = AgencyFocusCountrySerializer(many=True, source='agencyfocuscountry_set')
    activities = AgencyESGActivityReadSerializer(many=True, source='agencyesgactivity_set')
    memberships = AgencyMembershipSerializer(many=True, source='agencymembership_set')
    decisions = AgencyEQARDecisionSerializer(many=True, source='agencyeqardecision_set')
    country = CountrySelectSerializer()
    flags = AgencyFlagSerializer(many=True, source='agencyflag_set')
    update_log = AgencyUpdateLogSerializer(many=True, source='agencyupdatelog_set')

    def get_primary_name_acronym(self, obj):
        return "%s / %s" % (obj.name_primary, obj.acronym_primary)

    class Meta:
        model = Agency
        fields = '__all__'
