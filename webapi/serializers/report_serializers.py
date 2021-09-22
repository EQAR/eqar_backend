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
    institutions = serializers.SerializerMethodField()
    institution_relationship_context = serializers.SerializerMethodField()
    report_valid = serializers.SerializerMethodField()

    def get_institutions(self, obj):
        insitutions = obj.institutions.exclude(id=self.context['institution'])
        serializer = InstitutionListSerializer(instance=insitutions, many=True,
                                               context={'request': self.context['request']})
        return serializer.data

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

    def get_institution_relationship_context(self, obj):
        related_institutions = []

        for child_id in self.context['children']:
            inst = Institution.objects.get(pk=child_id)
            if obj.institutions.filter(pk=inst.pk).exists():
                related_institutions.append({
                    'id': inst.pk,
                    'relationship': 'child',
                    'name_primary': inst.name_primary
                })

        for parent_id in self.context['parents']:
            inst = Institution.objects.get(pk=parent_id)
            if obj.institutions.filter(pk=inst.pk).exists():
                related_institutions.append({
                    'id': inst.pk,
                    'relationship': 'parent',
                    'name_primary': inst.name_primary
                })

        return related_institutions

    class Meta:
        model = Report
        fields = ['institutions', 'agency_name', 'agency_acronym', 'agency_id', 'agency_url',
                  'agency_esg_activity', 'agency_esg_activity_type', 'name',
                  'report_valid', 'valid_from', 'valid_to', 'status', 'decision', 'summary', 'report_files',
                  'report_links', 'local_identifier', 'flag', 'institution_relationship_context']
