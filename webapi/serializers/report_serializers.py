import datetime

from datedelta import datedelta
from rest_framework import serializers
from institutions.models import Institution
from reports.models import Report, ReportFile


class ReportFileSerializer(serializers.ModelSerializer):
    languages = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ReportFile
        fields = ['file_display_name', 'file', 'languages']


class ReportSerializer(serializers.ModelSerializer):
    agency_url = serializers.HyperlinkedRelatedField(read_only=True, view_name="webapi-v1:agency-detail",
                                                     source='agency')
    agency_name = serializers.SlugRelatedField(source='agency', slug_field='name_primary', read_only=True)
    agency_acronym = serializers.SlugRelatedField(source='agency', slug_field='acronym_primary', read_only=True)
    agency_esg_activity = serializers.SlugRelatedField(slug_field='activity', read_only=True)
    report_files = ReportFileSerializer(many=True, read_only=True, source='reportfile_set')
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    flag = serializers.StringRelatedField()
    institution_relationship_context = serializers.SerializerMethodField()
    report_valid = serializers.SerializerMethodField()

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
        related_institution = {}

        for child_id in self.context['children']:
            inst = Institution.objects.get(pk=child_id)
            if obj.institutions.filter(pk=inst.pk).exists():
                related_institution['id'] = inst.pk
                related_institution['relationship'] = 'child'
                related_institution['name_primary'] = inst.name_primary
                related_institutions.append(related_institution)

        for parent_id in self.context['parents']:
            inst = Institution.objects.get(pk=parent_id)
            if obj.institutions.filter(pk=inst.pk).exists():
                related_institution['id'] = inst.pk
                related_institution['relationship'] = 'parent'
                related_institution['name_primary'] = inst.name_primary
                related_institutions.append(related_institution)

        return related_institutions

    class Meta:
        model = Report
        fields = ['agency_name', 'agency_acronym', 'agency_url', 'agency_esg_activity', 'report_valid', 'valid_from', 'valid_to', 'status', 'decision', 'report_files',
                  'local_identifier', 'name', 'flag', 'institution_relationship_context']
