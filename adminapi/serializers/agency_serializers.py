from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from adminapi.fields import PDFBase64File
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
        exclude = ('agency_name',)


class AgencyNameSerializer(WritableNestedModelSerializer):
    agency_name_versions = AgencyNameVersionSerializer(many=True, source='agencynameversion_set')

    class Meta:
        model = AgencyName
        exclude = ('agency',)


class AgencyPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyPhone
        fields = ('id', 'phone')


class AgencyEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyEmail
        fields = ('id', 'email')


class AgencyFocusCountryReadSerializer(serializers.ModelSerializer):
    country = CountrySelectSerializer()

    class Meta:
        model = AgencyFocusCountry
        exclude = ('agency',)


class AgencyFocusCountryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyFocusCountry
        exclude = ('agency',)


class AgencyESGActivityReadSerializer(serializers.ModelSerializer):
    activity_type = AgencyActivityTypeSerializer()

    class Meta:
        model = AgencyESGActivity
        exclude = ('agency',)


class AgencyESGActivityWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyESGActivity
        exclude = ('agency',)


class AgencyMembershipReadSerializer(serializers.ModelSerializer):
    association = AssociationSelectSerializer()

    class Meta:
        model = AgencyMembership
        exclude = ('agency',)


class AgencyMembershipWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyMembership
        exclude = ('agency',)


class AgencyEQARDecisionReadSerializer(serializers.ModelSerializer):
    decision_type = EQARDecisionTypeSelectSerializer()
    decision_file_name = serializers.SerializerMethodField(source='decision_file')
    decision_file_size = serializers.SerializerMethodField(source='decision_file')
    decision_file_extra_name = serializers.SerializerMethodField(source='decision_file_extra')
    decision_file_extra_size = serializers.SerializerMethodField(source='decision_file_extra')

    def get_decision_file_name(self, obj):
        return obj.decision_file.name

    def get_decision_file_extra_name(self, obj):
        return obj.decision_file_extra.name

    def get_decision_file_size(self, obj):
        try:
            return obj.decision_file.size
        except Exception:
            return 0

    def get_decision_file_extra_size(self, obj):
        try:
            return obj.decision_file_extra.size
        except Exception:
            return 0

    class Meta:
        model = AgencyEQARDecision
        fields = '__all__'


class AgencyEQARDecisionWriteSerializer(serializers.ModelSerializer):
    decision_file_name = serializers.CharField(required=False, allow_blank=True)
    decision_file_upload = PDFBase64File(required=False, source='decision_file')
    decision_file_extra_name = serializers.CharField(required=False, allow_blank=True)
    decision_file_extra_upload = PDFBase64File(required=False, source='decision_file_extra')

    def update(self, instance, validated_data):
        instance.decision_date = validated_data.get('decision_date', '')
        instance.decision_type = validated_data.get('decision_type', '')

        decision_file_name = validated_data.get('decision_file_name', '')
        decision_file = validated_data.get('decision_file', '')
        if decision_file:
            decision_file.name = decision_file_name
            instance.decision_file = decision_file

        decision_file_extra_name = validated_data.get('decision_file_extra_name', '')
        decision_file_extra = validated_data.get('decision_file_extra', '')
        if decision_file_extra:
            decision_file_extra.name = decision_file_extra_name
            instance.decision_file_extra = decision_file_extra

        instance.save()
        return instance

    class Meta:
        model = AgencyEQARDecision
        fields = ('id', 'agency', 'decision_date', 'decision_type',
                  'decision_file_name', 'decision_file_upload',
                  'decision_file_extra_name', 'decision_file_extra_upload')


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
    focus_countries = AgencyFocusCountryReadSerializer(many=True, source='agencyfocuscountry_set')
    activities = AgencyESGActivityReadSerializer(many=True, source='agencyesgactivity_set')
    memberships = AgencyMembershipReadSerializer(many=True, source='agencymembership_set')
    decisions = AgencyEQARDecisionReadSerializer(many=True, source='agencyeqardecision_set')
    country = CountrySelectSerializer()
    flags = AgencyFlagSerializer(many=True, source='agencyflag_set')
    update_log = serializers.SerializerMethodField()

    def get_primary_name_acronym(self, obj):
        return "%s / %s" % (obj.name_primary, obj.acronym_primary)

    def get_update_log(self, obj):
        queryset = obj.agencyupdatelog_set.order_by('updated_at')
        return AgencyUpdateLogSerializer(queryset, many=True, context=self.context).data

    class Meta:
        model = Agency
        fields = '__all__'


class AgencyWriteSerializer(WritableNestedModelSerializer):
    names = AgencyNameSerializer(many=True, source='agencyname_set')
    phone_numbers = AgencyPhoneSerializer(many=True, source='agencyphone_set')
    emails = AgencyEmailSerializer(many=True, source='agencyemail_set')
    focus_countries = AgencyFocusCountryWriteSerializer(many=True, source='agencyfocuscountry_set')
    activities = AgencyESGActivityWriteSerializer(many=True, source='agencyesgactivity_set')
    memberships = AgencyMembershipWriteSerializer(many=True, source='agencymembership_set', required=False)
    decisions = AgencyEQARDecisionWriteSerializer(many=True, source='agencyeqardecision_set')
    flags = AgencyFlagSerializer(many=True, source='agencyflag_set', required=False)

    class Meta:
        model = Agency
        fields = '__all__'
