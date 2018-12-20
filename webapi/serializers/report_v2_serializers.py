import datetime

from datedelta import datedelta
from rest_framework import serializers
from institutions.models import Institution
from reports.models import Report, ReportFile, ReportLink
from webapi.serializers.institution_serializers import InstitutionListSerializer


class ReportLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportLink
        fields = ['link_display_name', 'link']


class ReportFileSerializer(serializers.ModelSerializer):
    languages = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ReportFile
        fields = ['file_display_name', 'file', 'languages']


class ReportSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(slug_field='activity_description', read_only=True, source='agency_esg_activity')
    name_display = serializers.SerializerMethodField(method_name='generate_name_display')
    agency_id = serializers.PrimaryKeyRelatedField(source='agency', read_only=True)
    agency_url = serializers.HyperlinkedRelatedField(read_only=True, view_name="webapi-v1:agency-detail",
                                                     source='agency')
    agency_name = serializers.SlugRelatedField(source='agency', slug_field='name_primary', read_only=True)
    agency_acronym = serializers.SlugRelatedField(source='agency', slug_field='acronym_primary', read_only=True)
    agency_esg_activity = serializers.SlugRelatedField(slug_field='activity', read_only=True)
    agency_esg_activity_type = serializers.SerializerMethodField()
    report_files = ReportFileSerializer(many=True, read_only=True, source='reportfile_set')
    report_links = ReportLinkSerializer(many=True, read_only=True, source='reportlink_set')
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    flag = serializers.StringRelatedField()
    report_valid = serializers.SerializerMethodField()

    def generate_name_display(self, obj):
        institution = self.context['institution']
        report_type = self.context['report_type']
        programme = self.context.get('programme_name', "")
        programme_qf_ehea_level = self.context.get('qf_ehea_level', "")

        if institution in obj.institutions.all():
            if report_type == 'institutional':
                return "%s (by %s)" % (obj.agency_esg_activity.activity_description, obj.agency.acronym_primary)
            else:
                return "%s, %s" % (programme, programme_qf_ehea_level)
        else:
            institution_name_list = ", ".join([inst.name_primary.strip() for inst in obj.institutions.iterator()])
            if report_type == 'institutional':
                return "%s, %s (by %s)" % (obj.agency_esg_activity.activity_description, institution_name_list, obj.agency.acronym_primary)
            else:
                return "%s, %s, %s" % (programme, programme_qf_ehea_level, institution_name_list)

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

    class Meta:
        model = Report
        fields = ['agency_name', 'agency_acronym', 'agency_id', 'agency_url',
                  'agency_esg_activity', 'agency_esg_activity_type', 'name', 'name_display',
                  'report_valid', 'valid_from', 'valid_to', 'status', 'decision', 'report_files',
                  'report_links', 'local_identifier', 'flag']
