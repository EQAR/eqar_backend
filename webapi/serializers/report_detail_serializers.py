import datetime

from datedelta import datedelta
from institutions.models import Institution
from reports.models import Report
from programmes.models import Programme
from rest_framework import serializers

from webapi.serializers.report_v2_serializers import ReportFileSerializer, ReportLinkSerializer
from webapi.serializers.programme_v2_serializers import ProgrammeIdentifierSerializer


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'deqar_id', 'name_primary', 'website_link']


class ProgrammeSerializer(serializers.ModelSerializer):
    programme_identifiers = ProgrammeIdentifierSerializer(many=True, read_only=True, source='programmeidentifier_set')
    countries = serializers.StringRelatedField(many=True, read_only=True)
    qf_ehea_level = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Programme
        fields = ['name_primary', 'programme_identifiers', 'nqf_level', 'qf_ehea_level', 'countries']


class ReportDetailSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(slug_field='activity_description', read_only=True, source='agency_esg_activity')
    agency_id = serializers.PrimaryKeyRelatedField(source='agency', read_only=True)
    agency_url = serializers.HyperlinkedRelatedField(read_only=True, view_name="webapi-v1:agency-detail",
                                                     source='agency')
    agency_name = serializers.SlugRelatedField(source='agency', slug_field='name_primary', read_only=True)
    agency_acronym = serializers.SlugRelatedField(source='agency', slug_field='acronym_primary', read_only=True)
    agency_esg_activity = serializers.SlugRelatedField(slug_field='activity', read_only=True)
    agency_esg_activity_type = serializers.SerializerMethodField()
    report_files = ReportFileSerializer(many=True, read_only=True, source='reportfile_set')
    report_links = ReportLinkSerializer(many=True, read_only=True, source='reportlink_set')
    institutions = InstitutionSerializer(many=True)
    institutions_hierarchical = serializers.SerializerMethodField(source='institutions')
    institutions_historical = serializers.SerializerMethodField(source='institutions')
    programmes = ProgrammeSerializer(many=True, source='programme_set')
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    flag = serializers.StringRelatedField()
    report_valid = serializers.SerializerMethodField()

    def get_agency_esg_activity_type(self, obj):
        return obj.agency_esg_activity.activity_type.type

    def get_report_valid(self, obj):
        valid_from = obj.valid_from
        valid_to = obj.valid_to
        valid = True

        # Check if valid_from less than equal then todays date - 6 years and valid_to isn't set
        if valid_from <= datetime.date.today()-datedelta(years=6) and valid_to is None:
            valid = False

        # Check if valid_to lest than equal then todays date
        if valid_to:
            if valid_to <= datetime.date.today():
                valid = False

        return valid

    def get_institutions_hierarchical(self, obj):
        institutions = []
        for institution in obj.institutions.iterator():

            # Add Children
            for inst in institution.relationship_parent.all():
                s = InstitutionSerializer(inst.institution_child)
                i = s.data
                i['relationship'] = 'child'
                i['relationship_type'] = inst.relationship_type.type if inst.relationship_type else 'N/A'
                institutions.append(i)

            # Add Parents
            for inst in institution.relationship_child.all():
                s = InstitutionSerializer(inst.institution_parent)
                i = s.data
                i['relationship'] = 'parent'
                i['relationship_type'] = inst.relationship_type.type if inst.relationship_type else 'N/A'
                institutions.append(i)

        return institutions

    def get_institutions_historical(self, obj):
        institutions = []
        for institution in obj.institutions.iterator():

            # Add target
            for inst in institution.relationship_source.all():
                s = InstitutionSerializer(inst.institution_target)
                i = s.data
                i['relationship'] = 'target'
                i['relationship_type'] = inst.relationship_type.type_to
                i['relationship_date'] = inst.relationship_date
                institutions.append(i)

            # Add source
            for inst in institution.relationship_target.all():
                s = InstitutionSerializer(inst.institution_source)
                i = s.data
                i['relationship'] = 'source'
                i['relationship_type'] = inst.relationship_type.type_from
                i['relationship_date'] = inst.relationship_date
                institutions.append(i)

        return institutions

    class Meta:
        model = Report
        fields = ['agency_name', 'agency_acronym', 'agency_id', 'agency_url',
                  'agency_esg_activity', 'agency_esg_activity_type', 'name',
                  'institutions', 'institutions_hierarchical', 'institutions_historical', 'programmes',
                  'report_valid', 'valid_from', 'valid_to', 'status', 'decision', 'report_files',
                  'report_links', 'local_identifier', 'flag']