from rest_framework import serializers
from countries.models import Country, CountryQAARegulation, CountryHistoricalData, CountryQARequirement
from eqar_backend.serializers import HistoryFilteredListSerializer
from institutions.models import Institution
from reports.models import Report


class CountryListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:country-detail")

    class Meta:
        model = Country
        fields = ['id', 'url', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3']


class CountryReportListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:country-detail")
    institution_count = serializers.IntegerField(source='inst_count')

    class Meta:
        model = Country
        fields = ['id', 'url', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'institution_count']


class CountryLargeListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:country-detail")
    external_QAA_is_permitted = serializers.StringRelatedField()
    european_approach_is_permitted = serializers.StringRelatedField()
    agency_count = serializers.IntegerField()

    class Meta:
        model = Country
        fields = ['id', 'url', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'external_QAA_is_permitted',
                  'european_approach_is_permitted', 'eqar_governmental_member_start', 'agency_count']


class CountryQAARegulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryQAARegulation
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['regulation', 'regulation_url', 'regulation_valid_from', 'regulation_valid_to']


class CountryQARequirementSerializer(serializers.ModelSerializer):
    qa_requirement_type = serializers.StringRelatedField()

    class Meta:
        model = CountryQARequirement
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['qa_requirement', 'qa_requirement_type', 'qa_requirement_note',
                  'requirement_valid_from', 'requirement_valid_to']


class CountryHistoricalDataSerializer(serializers.ModelSerializer):
    field = serializers.StringRelatedField()

    class Meta:
        model = CountryHistoricalData
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['field', 'record_id', 'value', 'valid_from', 'valid_to']


class CountryDetailSerializer(serializers.ModelSerializer):
    qa_requirements = CountryQARequirementSerializer(many=True, read_only=True, source='countryqarequirement_set')
    qaa_regulations = CountryQAARegulationSerializer(many=True, read_only=True, source='countryqaaregulation_set')
    historical_data = CountryHistoricalDataSerializer(many=True, read_only=True, source='countryhistoricaldata_set')
    external_QAA_is_permitted = serializers.StringRelatedField()
    european_approach_is_permitted = serializers.StringRelatedField()
    report_count = serializers.SerializerMethodField()
    institution_count = serializers.SerializerMethodField()

    def get_report_count(self, obj):
        return Report.objects.filter(institutions__institutioncountry__country=obj).count()

    def get_institution_count(self, obj):
        return Institution.objects.filter(has_report=True, institutioncountry__country=obj).count()

    class Meta:
        model = Country
        fields = ['id', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3',
                  'ehea_is_member', 'eqar_governmental_member_start',
                  'qa_requirements', 'qa_requirement_note',
                  'external_QAA_is_permitted', 'external_QAA_note',
                  'eligibility', 'conditions', 'recognition',
                  'european_approach_is_permitted', 'european_approach_note',
                  'general_note', 'qaa_regulations',
                  'report_count', 'institution_count',
                  'historical_data']


class CountryCounterSerializer(serializers.Serializer):
    reports = serializers.IntegerField()
    institutions = serializers.IntegerField()


class CountryAgencySerializer(serializers.Serializer):
    agency_id = serializers.IntegerField()
    reports = serializers.IntegerField()
    institutions = serializers.IntegerField()


class CountryStatsSerializer(serializers.Serializer):
    country_counter = CountryCounterSerializer()
    country_agency_based_in_counter = CountryAgencySerializer(many=True, required=False)
    country_agency_focused_on_counter = CountryAgencySerializer(many=True, required=False)