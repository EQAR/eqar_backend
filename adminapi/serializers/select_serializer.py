from rest_framework import serializers

from agencies.models import Agency, AgencyESGActivity
from countries.models import Country
from lists.models import Language, Association, EQARDecisionType, IdentifierResource, PermissionType, QFEHEALevel


class AgencySelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ['id', 'acronym_primary']


class AgencyESGActivitySerializer(serializers.ModelSerializer):
    activity_type = serializers.StringRelatedField()

    class Meta:
        model = AgencyESGActivity
        fields = ['id', 'activity', 'activity_type']


class CountrySelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3']


class LanguageSelectSerializer(serializers.ModelSerializer):
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