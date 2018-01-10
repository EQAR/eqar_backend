from rest_framework import serializers
from countries.models import Country, CountryQAARegulation, CountryHistoricalData, CountryQARequirement


class CountryListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:country-detail")

    class Meta:
        model = Country
        fields = ['id', 'url', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3']


class CountryQAARegulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryQAARegulation
        fields = ['regulation', 'regulation_url']


class CountryQARequirementSerializer(serializers.ModelSerializer):
    qa_requirement_type = serializers.StringRelatedField()

    class Meta:
        model = CountryQARequirement
        fields = ['qa_requirement', 'qa_requirement_type', 'qa_requirement_note']


class CountryHistoricalDataSerializer(serializers.ModelSerializer):
    field = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = CountryHistoricalData
        fields = ['field', 'value', 'valid_from', 'valid_to']


class CountryDetailSerializer(serializers.ModelSerializer):
    qa_requirements = CountryQARequirementSerializer(many=True, read_only=True, source='countryqarequirement_set')
    qaa_regulations = CountryQAARegulationSerializer(many=True, read_only=True, source='countryqaaregulation_set')
    historical_data = CountryHistoricalDataSerializer(many=True, read_only=True, source='countryhistoricaldata_set')

    class Meta:
        model = Country
        fields = ['id', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'ehea_is_member',
                  'eqar_govermental_member_start', 'qa_requirements', 'qa_requirement_note',
                  'external_QAA_is_permitted', 'eligibility', 'conditions', 'recognition',
                  'external_QAA_permitted_note', 'european_approach_is_permitted', 'european_approach_note',
                  'general_note', 'qaa_regulations', 'historical_data']
