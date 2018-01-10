from rest_framework import serializers
from institutions.models import Institution, InstitutionIdentifier, InstitutionName, InstitutionETERRecord, \
    InstitutionHistoricalData


class InstitutionListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:institution-detail")
    eter_id = serializers.SlugRelatedField(read_only=True, slug_field='eter_id', source='eter')

    class Meta:
        model = Institution
        fields = ['id', 'eter_id', 'url', 'name_primary']


class InstitutionIdentifierSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField(read_only=True)
    resource = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = InstitutionIdentifier
        fields = ['identifier', 'agency', 'resource']


class InstitutionNameVersionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'translitertion']


class InstitutionNameSerializer(serializers.ModelSerializer):
    name_versions = InstitutionNameVersionSerializer(many=True, read_only=True, source='institutionnameversion_set')

    class Meta:
        model = InstitutionName
        fields = ['name_official', 'name_official_transliterated', 'name_english', 'name_versions', 'acronym',
                  'source_note', 'valid_to']


class InstitutionETERRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionETERRecord
        fields = ['eter_id', 'national_identifier', 'name', 'name_english', 'acronym', 'website', 'ISCED_lowest',
                  'ISCED_highest', 'valid_from_year', 'data_updated', 'eter_link']


class InstitutionHistoricalDataSerializer(serializers.ModelSerializer):
    field = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = InstitutionHistoricalData
        fields = ['field', 'value', 'valid_from', 'valid_to']


class InstitutionDetailSerializer(serializers.ModelSerializer):
    eter = InstitutionETERRecordSerializer()
    identifiers = InstitutionIdentifierSerializer(many=True, read_only=True, source='institutionidentifier_set')
    names = InstitutionNameSerializer(many=True, read_only=True, source='institutionname_set')
    countries = serializers.StringRelatedField()
    # nqf_levels = serializers.StringRelatedField(many=True, read_only=True, source='institutionnqflevel_set')
    qf_ehea_levels = serializers.StringRelatedField(many=True, read_only=True, source='institutionqfehealevel_set')
    historical_data = InstitutionHistoricalDataSerializer(many=True, read_only=True, source='institutionhistoricaldata_set')

    class Meta:
        model = Institution
        fields = ('id', 'eter', 'identifiers', 'website_link', 'names', 'countries', 'qf_ehea_levels', 'historical_data')
