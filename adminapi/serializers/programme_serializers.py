from drf_writable_nested import WritableNestedModelSerializer, UniqueFieldsMixin
from rest_framework import serializers

from adminapi.serializers.select_serializers import QFEHEALevelSelectSerializer, CountrySelectSerializer, \
    DegreeOutcomeSelectSerializer, ECTSCreditSelectSerializer, AssessmentSelectSerializer
from eqar_backend.serializer_fields.esco_serializer_field import ESCOSerializer
from eqar_backend.serializer_fields.isced_serializer_field import ISCEDSerializer
from programmes.models import Programme, ProgrammeName, ProgrammeLearningOutcome


class ProgrammeAlternativeNameSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    name_alternative = serializers.CharField(max_length=200, source='name', required=False)
    qualification_alternative = serializers.CharField(max_length=200, source='qualification',
                                                      allow_blank=True, required=False)

    class Meta:
        model = ProgrammeName
        fields = ['id', 'name_alternative', 'qualification_alternative', 'name_is_primary']


class ProgrammeLearningOutcomeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    learning_outcome = ESCOSerializer(required=False)

    class Meta:
        model = ProgrammeLearningOutcome
        fields = ['id', 'learning_outcome', 'learning_outcome_description']


class ProgrammeReadSerializer(serializers.ModelSerializer):
    alternative_names = ProgrammeAlternativeNameSerializer(many=True, required=False, source='programmename_set')
    qf_ehea_level = QFEHEALevelSelectSerializer(required=False, allow_null=True)
    countries = CountrySelectSerializer(many=True)
    degree_outcome = DegreeOutcomeSelectSerializer()
    workload_ects = ECTSCreditSelectSerializer()
    assessment_certification = AssessmentSelectSerializer()
    learning_outcomes = ProgrammeLearningOutcomeSerializer(many=True, required=False, source='programmelearningoutcome_set')
    field_study = ISCEDSerializer(required=False)

    class Meta:
        model = Programme
        fields = ['id', 'alternative_names', 'nqf_level', 'qf_ehea_level', 'countries',
                  'degree_outcome', 'workload_ects', 'assessment_certification', 'learning_outcomes',
                  'learning_outcome_description', 'field_study', 'mc_as_part_of_accreditation']


class ProgrammeWriteSerializer(WritableNestedModelSerializer):
    alternative_names = ProgrammeAlternativeNameSerializer(many=True, required=False, source='programmename_set')
    learning_outcomes = ProgrammeLearningOutcomeSerializer(many=True, required=False, source='programmelearningoutcome_set')
    field_study = ISCEDSerializer(required=False)

    class Meta:
        model = Programme
        fields = ['id', 'name_primary', 'alternative_names', 'nqf_level', 'qf_ehea_level', 'countries',
                  'degree_outcome', 'workload_ects', 'assessment_certification', 'learning_outcomes',
                  'learning_outcome_description', 'field_study', 'mc_as_part_of_accreditation']
