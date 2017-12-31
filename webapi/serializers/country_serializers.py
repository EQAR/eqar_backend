from rest_framework import serializers
from countries.models import Country


class CountryListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:country-detail")

    class Meta:
        model = Country
        fields = ['id', 'url', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3']


class CountryDetailSerializer(serializers.ModelSerializer):
    qa_requirement_type = serializers.StringRelatedField()

    class Meta:
        model = Country
        fields = ['id', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'ehea_is_member',
                  'eqar_govermental_member_start', 'qa_requirement', 'qa_requirement_type', 'qa_requirement_notes',
                  'external_QAA_is_permitted', 'eligibility', 'conditions', 'recognition',
                  'external_QAA_permitted_note', 'european_approach_is_permitted', 'european_approach_note',
                  'general_note']
