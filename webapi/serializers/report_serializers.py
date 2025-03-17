import datetime

from django.db.models import Q
from datedelta import datedelta
from rest_framework import serializers

from institutions.models import Institution
from reports.models import Report, ReportFile, ReportLink

from webapi.serializers.report_detail_serializers import InstitutionSerializer
from webapi.serializers.agency_serializers import ContributingAgencySerializer


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
    contributing_agencies = ContributingAgencySerializer(many=True)
    report_files = ReportFileSerializer(many=True, read_only=True, source='reportfile_set')
    report_links = ReportLinkSerializer(many=True, read_only=True, source='reportlink_set')
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    crossborder = serializers.SerializerMethodField()
    flag = serializers.StringRelatedField()
    institutions = serializers.SerializerMethodField()
    platforms = serializers.SerializerMethodField()
    report_valid = serializers.SerializerMethodField()

    def get_institutions(self, obj):
        insitutions = obj.institutions.exclude(id=self.context['institution'])
        serializer = InstitutionSerializer(instance=insitutions, many=True,
                                               context={'request': self.context['request']})
        return serializer.data

    def get_platforms(self, obj):
        platforms = obj.platforms.exclude(id=self.context['institution'])
        serializer = InstitutionSerializer(instance=platforms, many=True,
                                               context={'request': self.context['request']})
        return serializer.data

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
        if valid_from <= datetime.date.today()-datedelta(years=6) and valid_to is None:
            valid = False

        # Check if valid_to lest than equal then todays date
        if valid_to:
            if valid_to <= datetime.date.today():
                valid = False

        return valid


    class Meta:
        model = Report
        fields = ['id', 'institutions', 'agency_name', 'agency_acronym', 'agency_id', 'agency_url',
                  'platforms',
                  'contributing_agencies',
                  'agency_esg_activity', 'agency_esg_activity_type', 'name',
                  'report_valid', 'valid_from', 'valid_to', 'status', 'decision', 'crossborder', 'summary', 'report_files',
                  'report_links', 'local_identifier', 'other_comment', 'flag' ]
