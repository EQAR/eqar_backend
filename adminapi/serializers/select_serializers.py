from drf_writable_nested import UniqueFieldsMixin
from rest_framework import serializers

from agencies.models import Agency, AgencyESGActivity, AgencyActivityType
from countries.models import Country, CountryQARequirementType
from institutions.models import InstitutionHistoricalRelationshipType, InstitutionHierarchicalRelationshipType, \
    InstitutionOrganizationType
from lists.models import Language, Association, EQARDecisionType, IdentifierResource, PermissionType, QFEHEALevel, Flag, \
    Assessment, DegreeOutcome
from reports.models import ReportDecision, ReportStatus


class AgencySelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ['id', 'acronym_primary']


class AgencyESGActivitySerializer(serializers.ModelSerializer):
    agency = serializers.SlugRelatedField(read_only=True, slug_field='acronym_primary')
    activity_type = serializers.StringRelatedField()

    class Meta:
        model = AgencyESGActivity
        fields = ['id', 'agency', 'activity', 'activity_type']


class AgencyActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyActivityType
        fields = ['id', 'type']


class CountrySelectSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3']


class LanguageSelectSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'language_name_en', 'iso_639_1', 'iso_639_2']


class AssociationSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Association
        fields = ['id', 'association']


class EQARDecisionTypeSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = EQARDecisionType
        fields = ['id', 'type']


class IdentifierResourceSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentifierResource
        fields = ['id', 'resource']


class PermissionTypeSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionType
        fields = ['id', 'type']


class QFEHEALevelSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = QFEHEALevel
        fields = ['id', 'level', 'code']


class ReportDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDecision
        fields = ['id', 'decision']


class ReportStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportStatus
        fields = ['id', 'status']


class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        ref_name = 'FlagSelectSerializer'
        fields = ['id', 'flag']


class CountryQARequirementTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryQARequirementType
        fields = ['id', 'qa_requirement_type']


class InstitutionHierarchicalRelationshipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionHierarchicalRelationshipType
        fields = ['id', 'type']


class InstitutionHistoricalRelationshipTypeSerializer(serializers.ModelSerializer):
    relationship_type_id = serializers.IntegerField()
    relationship = serializers.CharField()
    institution_direction = serializers.CharField()

    class Meta:
        model = InstitutionHistoricalRelationshipType
        fields = ['id', 'relationship_type_id', 'relationship', 'institution_direction']


class InstitutionOrganizationTypeSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionOrganizationType
        fields = ['id', 'type']


class AssessmentSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['id', 'assessment']


class DegreeOutcomeSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DegreeOutcome
        fields = ['id', 'outcome']
