from datetime import datetime, date

from django.db.models import Q
from datedelta import datedelta
from institutions.models import Institution
from reports.models import Report
from programmes.models import Programme, ProgrammeIdentifier, ProgrammeName
from rest_framework import serializers

from webapi.serializers.report_v2_serializers import ReportFileSerializer, ReportLinkSerializer
from webapi.serializers.agency_serializers import ContributingAgencySerializer


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'deqar_id', 'name_primary', 'website_link']


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
    qf_ehea_level = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Programme
        fields = ['id', 'name_primary', 'programme_names', 'programme_identifiers',
                  'nqf_level', 'qf_ehea_level', 'countries']


class ReportDetailSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(slug_field='activity_description', read_only=True, source='agency_esg_activity')
    agency_id = serializers.PrimaryKeyRelatedField(source='agency', read_only=True)
    agency_url = serializers.HyperlinkedRelatedField(read_only=True, view_name="webapi-v1:agency-detail",
                                                     source='agency')
    agency_name = serializers.SlugRelatedField(source='agency', slug_field='name_primary', read_only=True)
    agency_acronym = serializers.SlugRelatedField(source='agency', slug_field='acronym_primary', read_only=True)
    agency_esg_activity = serializers.SlugRelatedField(slug_field='activity', read_only=True)
    agency_esg_activity_type = serializers.SerializerMethodField()
    contributing_agencies = ContributingAgencySerializer(many=True)
    report_files = ReportFileSerializer(many=True, read_only=True, source='reportfile_set')
    report_links = ReportLinkSerializer(many=True, read_only=True, source='reportlink_set')
    institutions = InstitutionSerializer(many=True)
    institutions_additional = serializers.SerializerMethodField(source='institutions')
    programmes = ProgrammeSerializer(many=True, source='programme_set')
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    crossborder = serializers.SerializerMethodField()
    flag = serializers.StringRelatedField()
    report_valid = serializers.SerializerMethodField()
    valid_to_calculated = serializers.SerializerMethodField()
    date_created = serializers.SerializerMethodField()
    date_updated = serializers.SerializerMethodField()

    def get_agency_esg_activity_type(self, obj):
        return obj.agency_esg_activity.activity_type.type

    def get_crossborder(self, obj):
        crossborder = False
        focus_countries = obj.agency.agencyfocuscountry_set
        for inst in obj.institutions.iterator():
            for ic in inst.institutioncountry_set.iterator():
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
        institutions = []
        for institution in obj.institutions.iterator():
            # Add children
            for inst in institution.relationship_parent.all():
                institutions.append(inst.institution_child.id)

            # Add parents
            for inst in institution.relationship_child.all():
                institutions.append(inst.institution_parent.id)

            # Add target
            for inst in institution.relationship_source.all():
                institutions.append(inst.institution_target.id)

            # Add source
            for inst in institution.relationship_target.all():
                institutions.append(inst.institution_source.id)

        return institutions

    def get_date_created(self, obj):
        return obj.created_at.isoformat()[:-3]+'Z'

    def get_date_updated(self, obj):
        return obj.updated_at.isoformat()[:-3]+'Z'

    def get_valid_to_calculated(self, obj):
        if obj.valid_to:
            valid_to = "%sZ" % datetime.combine(obj.valid_to, datetime.min.time()).isoformat()
            return valid_to
        else:
            valid_to = self._add_years(obj.valid_from, 5)
            valid_to = "%sZ" % datetime.combine(valid_to, datetime.min.time()).isoformat()
            return valid_to

    @staticmethod
    def _add_years(d, years):
        try:
            return d.replace(year=d.year + years)
        except ValueError:
            return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

    class Meta:
        model = Report
        fields = ['id', 'agency_name', 'agency_acronym', 'agency_id', 'agency_url',
                  'contributing_agencies',
                  'agency_esg_activity', 'agency_esg_activity_type', 'name',
                  'institutions', 'institutions_additional', 'programmes',
                  'report_valid', 'valid_from', 'valid_to', 'valid_to_calculated',
                  'status', 'decision', 'crossborder', 'summary',
                  'report_files', 'report_links',
                  'date_created', 'date_updated', 'local_identifier', 'other_comment', 'flag']