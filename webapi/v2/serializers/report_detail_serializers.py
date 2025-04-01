import datetime

from django.db.models import Q
from datedelta import datedelta
from institutions.models import Institution
from reports.models import Report
from agencies.models import AgencyESGActivity, AgencyActivityGroup
from programmes.models import Programme, ProgrammeIdentifier, ProgrammeName, ProgrammeLearningOutcome
from lists.models import DegreeOutcome, Assessment
from rest_framework import serializers

from webapi.v2.serializers.report_serializers import ReportFileSerializer, ReportLinkSerializer
from webapi.v2.serializers.agency_serializers import ContributingAgencySerializer


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'deqar_id', 'name_primary', 'website_link', 'is_other_provider']


class ProgrammeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammeName
        fields = ['name', 'name_is_primary', 'qualification']


class ProgrammeIdentifierSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField()

    class Meta:
        model = ProgrammeIdentifier
        fields = ['identifier', 'agency', 'resource']


class DegreeOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DegreeOutcome
        fields = ['id', 'outcome']


class ProgrammeLearningOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammeLearningOutcome
        fields = ['learning_outcome_esco']


class ProgrammeSerializer(serializers.ModelSerializer):
    programme_names = ProgrammeNameSerializer(many=True, read_only=True, source='programmename_set')
    programme_identifiers = ProgrammeIdentifierSerializer(many=True, read_only=True, source='programmeidentifier_set')
    countries = serializers.StringRelatedField(many=True, read_only=True)
    qf_ehea_level = serializers.StringRelatedField(read_only=True)
    degree_outcome = DegreeOutcomeSerializer(read_only=True)
    programme_type = serializers.SerializerMethodField()
    assessment_certification = serializers.SlugRelatedField(slug_field='assessment', queryset=Assessment.objects.all())
    learning_outcomes = ProgrammeLearningOutcomeSerializer(many=True, read_only=True, source='programmelearningoutcome_set')

    def get_programme_type(self, obj):
        return obj.get_programme_type()

    class Meta:
        model = Programme
        fields = ['id', 'name_primary', 'programme_names', 'programme_identifiers',
                  'nqf_level', 'qf_ehea_level', 'countries', 'programme_type',
                  'degree_outcome', 'workload_ects', 'assessment_certification', 'field_study',
                  'learning_outcomes', 'learning_outcome_description']


class EsgActivitySerializer(serializers.ModelSerializer):
    group_id = serializers.PrimaryKeyRelatedField(source='activity_group', read_only=True)
    activity = serializers.CharField(source='activity_group.activity')
    activity_type = serializers.CharField(source='activity_group.activity_type.type')

    class Meta:
        model = AgencyESGActivity
        fields = [
            'id',
            'group_id',
            'activity',
            'activity_description',
            'reports_link',
            'activity_type'
        ]


class ReportDetailSerializer(serializers.ModelSerializer):
    agency_id = serializers.PrimaryKeyRelatedField(source='agency', read_only=True)
    agency_url = serializers.HyperlinkedRelatedField(read_only=True, view_name="webapi-v2:agency-detail",
                                                     source='agency')
    agency_name = serializers.SlugRelatedField(source='agency', slug_field='name_primary', read_only=True)
    agency_acronym = serializers.SlugRelatedField(source='agency', slug_field='acronym_primary', read_only=True)
    agency_esg_activity = serializers.SerializerMethodField()
    agency_esg_activity_type = serializers.SerializerMethodField()
    agency_esg_activities = EsgActivitySerializer(many=True, read_only=True)
    contributing_agencies = ContributingAgencySerializer(many=True)
    report_files = ReportFileSerializer(many=True, read_only=True, source='reportfile_set')
    report_links = ReportLinkSerializer(many=True, read_only=True, source='reportlink_set')
    institutions = InstitutionSerializer(many=True)
    platforms = InstitutionSerializer(many=True)
    institutions_hierarchical = serializers.SerializerMethodField(source='institutions')
    institutions_historical = serializers.SerializerMethodField(source='institutions')
    programmes = ProgrammeSerializer(many=True, source='programme_set')
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    crossborder = serializers.SerializerMethodField()
    flag = serializers.StringRelatedField()
    report_valid = serializers.SerializerMethodField()

    def get_agency_esg_activity(self, obj):
        # Temporary fix, to prevent frontend from crashing
        if obj.agency_esg_activities.count() > 0:
            return obj.agency_esg_activities.first().activity
        else:
            return 'N/A'

    def get_agency_esg_activity_type(self, obj):
        # Temporary fix, to prevent frontend from crashing
        if obj.agency_esg_activities.count() > 0:
            return obj.agency_esg_activities.first().activity_type.type
        else:
            return 'N/A'

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
        fields = ['id', 'agency_name', 'agency_acronym', 'agency_id', 'agency_url',
                  'contributing_agencies',
                  'agency_esg_activity', 'agency_esg_activity_type', 'agency_esg_activities',
                  'institutions', 'institutions_hierarchical', 'institutions_historical', 'programmes',
                  'platforms',
                  'report_valid', 'valid_from', 'valid_to', 'status', 'decision', 'crossborder', 'summary', 'report_files',
                  'report_links', 'local_identifier', 'other_comment', 'flag']
