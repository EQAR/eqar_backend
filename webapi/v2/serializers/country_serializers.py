from django.db.models import Q
from rest_framework import serializers
from agencies.models import AgencyActivityGroup
from countries.models import Country, CountryQAARegulation, CountryQARequirement, CountryQARequirementGroup, \
    CountryInstitutionType, CountryIncomingTneRegulation
from eqar_backend.serializers import HistoryFilteredListSerializer
from institutions.models import Institution, InstitutionCountry
from reports.models import Report


class CountryListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v2:country-detail")

    class Meta:
        model = Country
        fields = ['id', 'url', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3']


class CountryReportListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v2:country-detail")
    institution_count = serializers.IntegerField(source='inst_count')
    institution_total = serializers.SerializerMethodField()
    institution_eter = serializers.SerializerMethodField()
    ehea_key_commitment = serializers.StringRelatedField()
    reports_total = serializers.SerializerMethodField()

    def get_institution_total(self, obj):
        return Institution.objects.filter(institutioncountry__country__id=obj.id).count()

    def get_institution_eter(self, obj):
        return Institution.objects.filter(Q(institutioncountry__country__id=obj.id) & Q(eter_id__isnull=False)).count()

    def get_reports_total(self, obj):
        return Report.objects.filter(institutions__institutioncountry__country__id=obj.id).count()

    class Meta:
        model = Country
        fields = ['id', 'url', 'name_english', 'ehea_is_member', 'iso_3166_alpha2', 'iso_3166_alpha3',
                  'has_full_institution_list', 'ehea_key_commitment',
                  'institution_count', 'institution_total', 'institution_eter', 'reports_total']


class CountryLargeListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v2:country-detail")
    external_QAA_is_permitted = serializers.StringRelatedField()
    european_approach_is_permitted = serializers.StringRelatedField()
    ehea_key_commitment = serializers.StringRelatedField()
    agency_count = serializers.IntegerField()

    class Meta:
        model = Country
        fields = ['id', 'url', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'external_QAA_is_permitted',
                  'european_approach_is_permitted', 'has_full_institution_list', 'ehea_key_commitment',
                  'eqar_governmental_member_start', 'agency_count']


class CountryQAARegulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryQAARegulation
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['regulation', 'regulation_url', 'regulation_valid_from', 'regulation_valid_to']


class ControlledListSerializer(serializers.Serializer):
    """
    Serializes an entry of any controlled list (lists.models.ControlledList).
    """
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    uri = serializers.URLField(read_only=True)
    description = serializers.CharField(read_only=True)


class CountryQARequirementActivityGroupSerializer(serializers.ModelSerializer):
    activity_type = serializers.StringRelatedField()

    class Meta:
        model = AgencyActivityGroup
        fields = ['id', 'activity', 'activity_type']


class CountryInstitutionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryInstitutionType
        fields = ['id', 'name_national', 'name_english', 'eter_category_standard']


class CountryQARequirementDetailSerializer(serializers.ModelSerializer):
    activity_group = CountryQARequirementActivityGroupSerializer(read_only=True)
    qf_ehea_levels = serializers.StringRelatedField(many=True)
    cbqa_possible = ControlledListSerializer(read_only=True)
    cbqa_approval = ControlledListSerializer(many=True, read_only=True)
    cbqa_requirements = ControlledListSerializer(many=True, read_only=True)
    cbqa_criteria = ControlledListSerializer(read_only=True)
    cbqa_recognition = ControlledListSerializer(read_only=True)
    ea_possible = ControlledListSerializer(read_only=True)

    class Meta:
        model = CountryQARequirement
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['id', 'activity_group', 'duration', 'initial_only',
                  'fields_of_education', 'qf_ehea_levels', 'full_degrees', 'micro_credentials',
                  'qa_requirement_note', 'requirement_valid_from', 'requirement_valid_to',
                  'cbqa_possible', 'cbqa_approval', 'cbqa_requirements', 'cbqa_other_requirements_note',
                  'cbqa_criteria', 'cbqa_recognition',
                  'ea_possible', 'ea_note']


class CountryQARequirementGroupSerializer(serializers.ModelSerializer):
    institution_types = CountryInstitutionTypeSerializer(many=True, read_only=True)
    requirements = CountryQARequirementDetailSerializer(many=True, read_only=True)
    regulations = CountryQAARegulationSerializer(many=True, read_only=True)
    outgoing_tne_possible = ControlledListSerializer(read_only=True)
    outgoing_tne_approval = ControlledListSerializer(many=True, read_only=True)
    outgoing_tne_qa = ControlledListSerializer(read_only=True)
    mc_qa = ControlledListSerializer(many=True, read_only=True)

    class Meta:
        model = CountryQARequirementGroup
        fields = ['id', 'institution_types', 'combination_logic', 'requirements', 'regulations',
                  'outgoing_tne_possible', 'outgoing_tne_conditions', 'outgoing_tne_approval', 'outgoing_tne_qa',
                  'mc_possible', 'mc_credit_limit', 'mc_qa', 'mc_qa_note']


class CountryIncomingTneRegulationSerializer(serializers.ModelSerializer):
    origin_groups = ControlledListSerializer(many=True, read_only=True)
    incoming_tne_possible = ControlledListSerializer(read_only=True)
    incoming_tne_approval = ControlledListSerializer(many=True, read_only=True)
    incoming_tne_qa = ControlledListSerializer(read_only=True)

    class Meta:
        model = CountryIncomingTneRegulation
        fields = ['id', 'origin_groups', 'incoming_tne_possible', 'incoming_tne_conditions',
                  'incoming_tne_approval', 'incoming_tne_qa']


class CountryBaseDetailSerializer(serializers.ModelSerializer):
    """
    Country details without the structured QA requirements, TNE and micro-credential information.
    """
    qaa_regulations = serializers.SerializerMethodField()
    external_QAA_is_permitted = serializers.StringRelatedField()
    european_approach_is_permitted = serializers.StringRelatedField()
    ehea_key_commitment = serializers.StringRelatedField()
    report_count = serializers.SerializerMethodField()
    institution_count = serializers.SerializerMethodField()

    def get_qaa_regulations(self, obj):
        # regulations attached to a QA requirements group are listed under that group instead
        regulations = obj.countryqaaregulation_set.filter(group__isnull=True)
        return CountryQAARegulationSerializer(regulations, many=True, context=self.context).data

    def get_report_count(self, obj):
        return Report.objects.filter(institutions__institutioncountry__country=obj).count()

    def get_institution_count(self, obj):
        return Institution.objects.filter(has_report=True, institutioncountry__country=obj).distinct().count()

    class Meta:
        model = Country
        fields = ['id', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3',
                  'ehea_is_member', 'eqar_governmental_member_start',
                  'qa_requirement_note',
                  'external_QAA_is_permitted', 'european_approach_is_permitted',
                  'has_full_institution_list', 'ehea_key_commitment',
                  'general_note', 'qaa_regulations',
                  'report_count', 'institution_count']


class CountryDetailSerializer(CountryBaseDetailSerializer):
    qa_requirement_groups = CountryQARequirementGroupSerializer(many=True, read_only=True)
    incoming_tne_regulations = CountryIncomingTneRegulationSerializer(many=True, read_only=True)

    class Meta(CountryBaseDetailSerializer.Meta):
        fields = CountryBaseDetailSerializer.Meta.fields + [
            'lrc_signatory_date', 'qf_ehea_alignment_date', 'eqf_alignment_date',
            'qa_requirement_groups', 'incoming_tne_regulations',
        ]
