import json
from datetime import datetime, date

from datedelta import datedelta
from django.db.models import Q
from rest_framework import serializers

from countries.models import Country
from institutions.models import Institution
from programmes.models import Programme
from reports.models import Report


class ISODateField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%SZ")
        if isinstance(value, date):
            return value.strftime("%Y-%m-%dT00:00:00Z")


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'deqar_id', 'name_primary', 'website_link']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'ehea_is_member']


class ProgrammeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programme
        fields = ['id', 'name_primary', 'nqf_level', 'qf_ehea_level']


class ReportIndexerSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    agency = serializers.PrimaryKeyRelatedField(read_only=True)
    agency_url = serializers.CharField(source='agency.website_link')
    agency_esg_activity_type = serializers.CharField(source='agency_esg_activity.activity_type.type')
    country = serializers.SerializerMethodField()
    contributing_agencies = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    crossborder = serializers.SerializerMethodField()
    date_created = ISODateField(read_only=True, source='created_at')
    date_updated = ISODateField(read_only=True, source='updated_at')
    decision = serializers.CharField(source='decision.decision')
    flag_level = serializers.CharField(source='flag.flag')
    institutions = InstitutionSerializer(read_only=True, many=True)
    institutions_additional = serializers.SerializerMethodField()
    name = serializers.CharField(source='agency_esg_activity.activity_description')
    programmes = ProgrammeSerializer(many=True, source='programme_set')
    report_valid = serializers.SerializerMethodField()
    status = serializers.CharField(source='status.status')
    valid_from = ISODateField(read_only=True)
    valid_to = serializers.SerializerMethodField()
    valid_to_calculated = serializers.SerializerMethodField()

    # Search fields
    id_search = serializers.CharField(source='id')
    country_search = serializers.SerializerMethodField()
    city_search = serializers.SerializerMethodField(method_name='get_city')
    programme_name_search = serializers.SerializerMethodField()

    # ID fields
    agency_id = serializers.SerializerMethodField()
    activity_id = serializers.PrimaryKeyRelatedField(source='agency_esg_activity', read_only=True)
    activity_type_id = serializers.PrimaryKeyRelatedField(source='agency_esg_activity.activity_type', read_only=True)
    institution_id = serializers.SerializerMethodField()
    country_id = serializers.SerializerMethodField()
    language_id = serializers.SerializerMethodField()
    status_id = serializers.PrimaryKeyRelatedField(source='status', read_only=True)
    decision_id = serializers.PrimaryKeyRelatedField(source='decision', read_only=True)

    # Sort fields
    id_sort = serializers.CharField(source="id")
    name_sort = serializers.CharField(source='agency_esg_activity.activity_description')

    # Facet fields
    activity_type_facet = serializers.CharField(source='agency_esg_activity.activity_type.type')
    decision_facet = serializers.CharField(source='decision.decision')
    language_facet = serializers.SerializerMethodField()
    flag_level_facet = serializers.CharField(source='flag.flag')
    crossborder_facet = serializers.SerializerMethodField(method_name='get_crossborder')
    status_facet = serializers.CharField(source='status.status')

    # Return valid_to date
    def get_valid_to(self, obj):
        if obj.valid_to:
            return "%sZ" % datetime.combine(obj.valid_to, datetime.min.time()).isoformat()
        else:
            return None

    # Calculated valid_to date (valid_from + 5 years if valid_to doesn't exists)
    def get_valid_to_calculated(self, obj):
        if obj.valid_to:
            return "%sZ" % datetime.combine(obj.valid_to, datetime.min.time()).isoformat()
        else:
            valid_to = self._add_years(obj.valid_from, 5)
            return "%sZ" % datetime.combine(valid_to, datetime.min.time()).isoformat()

    # Get country records
    def get_country(self, obj):
        countries = []
        for inst in obj.institutions.all():
            for ic in inst.institutioncountry_set.all():
                serializer = CountrySerializer(ic.country)
                countries.append(serializer.data)
        for programme in obj.programme_set.all():
            for country in programme.countries.all():
                serializer = CountrySerializer(country)
                countries.append(serializer.data)
        return countries

    # Get crossborder
    def get_crossborder(self, obj):
        crossborder = False
        focus_countries = obj.agency.agencyfocuscountry_set
        for inst in obj.institutions.all():
            for ic in inst.institutioncountry_set.all():
                if focus_countries.filter(Q(country__id=ic.country.id) & Q(country_is_crossborder=True)):
                    crossborder = True
        return crossborder

    def get_report_valid(self, obj):
        valid_from = obj.valid_from
        valid_to = obj.valid_to
        valid = True

        # Check if valid_from less than equal then todays date - 6 years and valid_to isn't set
        if valid_from <= date.today()-datedelta(years=6) and valid_to is None:
            valid = False

        # Check if valid_to lest than equal then todays date
        if valid_to:
            if valid_to <= date.today():
                valid = False

        return valid

    def get_institutions_additional(self, obj):
        institutions_additional = []
        for inst in obj.institutions.all():
            for i in inst.relationship_parent.all():
                institutions_additional.append(i.institution_child.id)
            for i in inst.relationship_child.all():
                institutions_additional.append(i.institution_parent.id)
            for i in inst.relationship_source.all():
                institutions_additional.append(i.institution_target.id)
            for i in inst.relationship_target.all():
                institutions_additional.append(i.institution_source.id)
        return institutions_additional

    def get_country_search(self, obj):
        countries = []
        for inst in obj.institutions.all():
            for c in inst.institutioncountry_set.all():
                countries.append(c.country.name_english)
        for programme in obj.programme_set.all():
            for c in programme.countries.all():
                countries.append(c.country.name_english)
        return countries

    # Get city records
    def get_city(self, obj):
        cities = []
        for programme in obj.programme_set.all():
            for c in programme.countries.all():
                cities.append(c.city)
        return cities

    def get_programme_name_search(self, obj):
        programme_names = []
        for programme in obj.programme_set.all():
            for pname in programme.programmename_set.iterator():
                programme_names.append(pname.name.strip())
        return programme_names

    def get_agency_id(self, obj):
        agency_ids = [obj.agency.id]
        for agency in obj.contributing_agencies.all():
            agency_ids.append(agency.id)
        return agency_ids

    def get_institution_id(self, obj):
        institution_ids = []
        for inst in obj.institutions.all():
            institution_ids.append(inst.id)
            for i in inst.relationship_parent.all():
                institution_ids.append(i.id)
            for i in inst.relationship_child.all():
                institution_ids.append(i.id)
            for i in inst.relationship_source.all():
                institution_ids.append(i.id)
            for i in inst.relationship_target.all():
                institution_ids.append(i.id)
        return institution_ids

    def get_country_id(self, obj):
        country_ids = []
        for inst in obj.institutions.all():
            for ic in inst.institutioncountry_set.all():
                country_ids.append(ic.country.id)
        for programme in obj.programme_set.all():
            for country in programme.countries.all():
                country_ids.append(country.id)
        return country_ids

    def get_language_id(self, obj):
        languages = []
        for rf in obj.reportfile_set.all():
            for lang in rf.languages.all():
                languages.append(lang.id)
        return languages

    def get_language_facet(self, obj):
        languages = []
        for rf in obj.reportfile_set.all():
            for lang in rf.languages.all():
                languages.append(lang.language_name_en)
        return languages

    @staticmethod
    def _add_years(d, years):
        try:
            return d.replace(year=d.year + years)
        except ValueError:
            return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

    class Meta:
        model = Report
        exclude = ['agency_esg_activity', 'summary',
                   'flag', 'flag_log',
                   'other_comment', 'internal_note',
                   'created_at', 'created_by', 'updated_at', 'updated_by']