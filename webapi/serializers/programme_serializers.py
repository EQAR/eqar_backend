from rest_framework import serializers

from programmes.models import Programme, ProgrammeName, ProgrammeIdentifier
from lists.models import DegreeOutcome, Assessment

from webapi.serializers.report_serializers import ReportSerializer
from webapi.serializers.report_detail_serializers import DegreeOutcomeSerializer, ProgrammeLearningOutcomeSerializer


class ProgrammeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammeName
        fields = ['name', 'name_is_primary', 'qualification']


class ProgrammeIdentifierSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField()

    class Meta:
        model = ProgrammeIdentifier
        fields = ['identifier', 'agency', 'resource']


class ProgrammeSerializer(serializers.ModelSerializer):
    programme_names = ProgrammeNameSerializer(many=True, read_only=True, source='programmename_set')
    programme_identifiers = ProgrammeIdentifierSerializer(many=True, read_only=True, source='programmeidentifier_set')
    countries = serializers.StringRelatedField(many=True, read_only=True)
    report = ReportSerializer()
    qf_ehea_level = serializers.StringRelatedField(read_only=True)
    degree_outcome = DegreeOutcomeSerializer(read_only=True)
    programme_type = serializers.SerializerMethodField()
    assessment_certification = serializers.SlugRelatedField(slug_field='assessment', queryset=Assessment.objects.all())
    learning_outcomes = ProgrammeLearningOutcomeSerializer(many=True, read_only=True, source='programmelearningoutcome_set')

    def get_programme_type(self, obj):
        return obj.get_programme_type()

    class Meta:
        model = Programme
        fields = ['report', 'id', 'name_primary', 'programme_names', 'programme_identifiers',
                  'nqf_level', 'qf_ehea_level', 'countries', 'programme_type',
                  'degree_outcome', 'workload_ects', 'assessment_certification', 'field_study',
                  'learning_outcomes', 'learning_outcome_description']

