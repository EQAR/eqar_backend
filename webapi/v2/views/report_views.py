import datetime
import json
import re

from django.utils.decorators import method_decorator

from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema

from webapi.inspectors.report_search_inspector import ReportSearchInspector

from datedelta import datedelta
from django.db.models import Q
from rest_framework import generics
from rest_framework.exceptions import ParseError
from django.shortcuts import get_object_or_404

from eqar_backend.serializer_fields.boolean_extended_serializer_field import BooleanExtendedField

from webapi.v2.views.meili_solr_view import MeiliSolrBackportView

from lists.models import Language, QFEHEALevel
from agencies.models import Agency, AgencyActivityGroup
from institutions.models import Institution
from reports.models import Report, ReportStatus, ReportDecision
from programmes.models import Programme

from webapi.v2.serializers.report_detail_serializers import ReportDetailSerializer
from reports.serializers.report_meili_indexer_serializer import ReportIndexerSerializer
from programmes.serializers.programme_indexer_serializer import ProgrammeIndexerSerializer


class ReportFilterClass(filters.FilterSet):
    """
    Filters for all reports (used for institutional and programme views)
    """
    agency = filters.ModelChoiceFilter(label='Agency (acronym)',
                queryset=Agency.objects.all(),
                to_field_name='acronym_primary')
    activity_group_id = filters.ModelChoiceFilter(label='Reports in ESG Activity Group (ID)',
                queryset=AgencyActivityGroup.objects.all(),
                to_field_name='id')
    status = filters.ModelChoiceFilter(label='Reports with specified status',
                queryset=ReportStatus.objects.all(),
                to_field_name='status')
    decision = filters.ModelChoiceFilter(label='Reports with specified Decision',
                queryset=ReportDecision.objects.all(),
                to_field_name='decision')
    cross_border = filters.BooleanFilter(label='Only cross-border reports')
    language = filters.ModelChoiceFilter(label='Only reports in specified language (name)',
                queryset=Language.objects.all(),
                to_field_name='language_name_en')
    valid_on = filters.DateFilter(label='Reports that are/were valid on the given date')

    ordering = OrderingFilter(
        fields=(
            "valid_from",
            "valid_to_calculated",
            "date_created",
            "date_updated",
        ),
        field_labels={
            "valid_from": "Report date",
            "valid_to_calculated": "Valid to date",
            "date_created": "Date of upload to DEQAR",
            "date_updated": "Date of last update",
        }
    )

class ProgrammeFilterClass(ReportFilterClass):
    """
    Additional filters for programmes
    """
    query = filters.CharFilter(label='Search programme (name, qualification)')
    qf_ehea_level = filters.ModelChoiceFilter(label='QF-EHEA level',
                queryset=QFEHEALevel.objects.all(),
                to_field_name='level')
    degree_outcome = filters.BooleanFilter(label='Programmes leading to a full recognised degree')

    ordering = OrderingFilter(
        fields=(
            "programme_sort",
            "valid_from",
            "valid_to_calculated",
            "date_created",
            "date_updated",
        ),
        field_labels={
            "programme_sort": "Programme name",
            "valid_from": "Report date",
            "valid_to_calculated": "Valid to date",
            "date_created": "Date of upload to DEQAR",
            "date_updated": "Date of last update",
        }
    )



@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[ReportSearchInspector],
    responses={
        400: 'Bad request, e.g. some filter parameters could not be parsed',
        404: 'Institution could not be found',
    }
))
class InstitutionalReportsByInstitution(MeiliSolrBackportView):
    """
    Lists the institutional level reports for one institution
    """
    queryset = Report.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ReportFilterClass
    serializer_class = ReportIndexerSerializer

    MEILI_INDEX = 'INDEX_REPORTS'
    ORDERING_MAPPING = {
        "date_created": "created_at",
        "date_updated": "updated_at",
        "valid_from": "valid_from",
        "valid_to_calculated": "valid_to_calculated",
    }
    FACET_NAMES = {
        'agency.id': 'agency_facet',
        'contributing_agencies.id': 'agency_facet',
        'agency_esg_activities.group_id': 'activity_facet',
        'status': 'status_facet',
        'decision': 'decision_facet',
        'report_files.languages': 'language_facet',
        'crossborder': 'crossborder_facet',
    }
    FACET_LOOKUP = {
        'agency.id':                  { 'model': Agency,            'attribute': 'acronym_primary' },
        'contributing_agencies.id':   { 'model': Agency,            'attribute': 'acronym_primary' },
        'agency_esg_activities.group_id':    { 'model': AgencyActivityGroup, 'attribute': 'activity' },
    }

    def make_filters(self, request):
        institution = get_object_or_404(Institution, pk=self.kwargs['institution'])

        institution_filters = [
            f'institutions.id = {institution.id}',
            f'platforms.id = {institution.id}',
        ]

        # add reports of sub-units (faculties etc.)
        for rel in institution.relationship_parent.exclude(relationship_type__type='educational platform'):
            this_filter = f'( institutions.id = {rel.institution_child.id} OR platforms.id = {rel.institution_child.id} )'
            if rel.valid_from:
                this_filter += f' AND report.valid_to_calculated >= {datetime.combine(rel.valid_from, datetime.min.time()).timestamp()}'
            if rel.valid_to:
                this_filter += f' AND report.valid_from <= {datetime.combine(rel.valid_to, datetime.min.time()).timestamp()}'
            institution_filters.append(this_filter)

        # add reports of historically related institutions
        for rel in institution.relationship_source.filter(relationship_type__type_from='succeeded'):
            institution_filters.append(f'institutions.id = {rel.institution_target.id} AND report.valid_to_calculated >= {datetime.combine(rel.relationship_date, datetime.min.time()).timestamp()}')
        for rel in institution.relationship_target.filter(relationship_type__type_to='absorbed'):
            institution_filters.append(f'institutions.id = {rel.institution_source.id} AND report.valid_to_calculated >= {datetime.combine(rel.relationship_date, datetime.min.time()).timestamp()}')

        filters = [
            institution_filters,
            'agency_esg_activities.type IN [ "institutional", "institutional/programme" ]',
            'flag != "high level"',
        ]

        if agency_id := self.lookup_object(Agency, 'acronym_primary', 'agency', 'id', 'agency_id'):
            filters.append(f'agency.id = {agency_id} OR contributing_agencies.id = {agency_id}')

        if activity_group_ids := self.lookup_object(AgencyActivityGroup, 'activity', 'activity_group', 'id', 'activity_group_id', multi=True):
            filters.append(f'agency_esg_activities.group_id IN [ {activity_group_ids} ]')

        if status := self.lookup_object(ReportStatus, 'id', 'status_id', 'status', 'status'):
            filters.append(f'status = "{status}"')

        if decision := self.lookup_object(ReportDecision, 'id', 'decision_id', 'decision', 'decision'):
            filters.append(f'decision = "{decision}"')

        if language := self.lookup_object(Language, 'id', 'language_id', 'language_name_en', 'language'):
            filters.append(f'report_files.languages = "{language}"')

        if cross_border := request.query_params.get('cross_border', None):
            filters.append(f'crossborder = {BooleanExtendedField.to_internal_value(None, cross_border)}')

        if valid_on := request.query_params.get('valid_on', False):
            try:
                filters.append(f'valid_from <= {int(datetime.datetime.fromisoformat(valid_on).timestamp())}')
                filters.append(f'valid_to_calculated >= {int(datetime.datetime.fromisoformat(valid_on).timestamp())}')
            except ValueError:
                raise ParseError(detail=f'value [{valid_on}] for year cannot be parsed to datetime')

        return filters

    def convert_hit(self, r):
        """
        convert result structure
        """
        # date formats
        r['valid_from'] = self.timestamp_to_isodatetime(r['valid_from'])
        r['valid_to_calculated'] = self.timestamp_to_isodatetime(r['valid_to_calculated'])
        r['valid_to'] = self.timestamp_to_isodatetime(r['valid_to'])
        r['created_at'] = self.timestamp_to_isodatetime(r['created_at'])
        r['updated_at'] = self.timestamp_to_isodatetime(r['updated_at'])
        for i in r['institutions']:
            for l in i['locations']:
                l['country_valid_from'] = self.timestamp_to_isodatetime(l['country_valid_from'])
                l['country_valid_to'] = self.timestamp_to_isodatetime(l['country_valid_to'])

        # make file paths absolute
        for f in r["report_files"]:
            if "file" in f:
                f["file"] = self.request.build_absolute_uri(f['file'])

        return r


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[ReportSearchInspector],
    responses={
        400: 'Bad request, e.g. some filter parameters could not be parsed',
        404: 'Institution could not be found',
    }
))
class ProgrammesByInstitution(MeiliSolrBackportView):
    """
    Searches or lists the programmes of one institution
    """
    queryset = Programme.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProgrammeFilterClass
    serializer_class = ProgrammeIndexerSerializer

    MEILI_INDEX = 'INDEX_PROGRAMMES'
    ORDERING_MAPPING = {
        "name": "name_primary",
        "date_created": "report.created_at",
        "date_updated": "report.updated_at",
        "valid_from": "report.valid_from",
        "valid_to_calculated": "report.valid_to_calculated",
    }
    FACET_NAMES = {
        'report.agency.id': 'agency_facet',
        'report.contributing_agencies.id': 'agency_facet',
        'report.agency_esg_activities.group_id': 'activity_facet',
        'report.status': 'status_facet',
        'report.decision': 'decision_facet',
        'report.report_files.languages': 'language_facet',
        'report.crossborder': 'crossborder_facet',
        'degree_outcome': 'degree_outcome_facet',
        'programme_type': 'programme_type_facet'
    }
    FACET_LOOKUP = {
        'report.agency.id':                  { 'model': Agency,            'attribute': 'acronym_primary' },
        'report.contributing_agencies.id':   { 'model': Agency,            'attribute': 'acronym_primary' },
        'report.agency_esg_activities.group_id':    { 'model': AgencyActivityGroup, 'attribute': 'activity' },
    }


    def make_filters(self, request):
        institution = get_object_or_404(Institution, pk=self.kwargs['institution'])

        institution_filters = [
            f'institutions = {institution.id}',
            f'platforms = {institution.id}',
        ]

        # add reports of sub-units (faculties etc.)
        for rel in institution.relationship_parent.exclude(relationship_type__type='educational platform'):
            this_filter = f'( institutions = {rel.institution_child.id} OR platforms = {rel.institution_child.id} )'
            if rel.valid_from:
                this_filter += f' AND report.valid_to_calculated >= {datetime.combine(rel.valid_from, datetime.min.time()).timestamp()}'
            if rel.valid_to:
                this_filter += f' AND report.valid_from <= {datetime.combine(rel.valid_to, datetime.min.time()).timestamp()}'
            institution_filters.append(this_filter)

        # add reports of historically related institutions
        for rel in institution.relationship_source.filter(relationship_type__type_from='succeeded'):
            institution_filters.append(f'institutions = {rel.institution_target.id} AND report.valid_to_calculated >= {datetime.combine(rel.relationship_date, datetime.min.time()).timestamp()}')
        for rel in institution.relationship_target.filter(relationship_type__type_to='absorbed'):
            institution_filters.append(f'institutions = {rel.institution_source.id} AND report.valid_to_calculated >= {datetime.combine(rel.relationship_date, datetime.min.time()).timestamp()}')

        filters = [
            institution_filters,
            'report.agency_esg_activities.type IN [ "programme", "joint programme", "institutional/programme" ]',
            'report.flag != "high level"',
        ]

        if agency_id := self.lookup_object(Agency, 'acronym_primary', 'agency', 'id', 'agency_id'):
            filters.append(f'report.agency.id = {agency_id} OR report.contributing_agencies.id = {agency_id}')

        if activity_group_ids := self.lookup_object(AgencyActivityGroup, 'activity', 'activity_group', 'id', 'activity_group_id', multi=True):
            filters.append(f'report.agency_esg_activities.group_id IN [ {activity_group_ids} ]')

        if status := self.lookup_object(ReportStatus, 'id', 'status_id', 'status', 'status'):
            filters.append(f'report.status = "{status}"')

        if decision := self.lookup_object(ReportDecision, 'id', 'decision_id', 'decision', 'decision'):
            filters.append(f'report.decision = "{decision}"')

        if language := self.lookup_object(Language, 'id', 'language_id', 'language_name_en', 'language'):
            filters.append(f'report.report_files.languages = "{language}"')

        if cross_border := request.query_params.get('cross_border', None):
            filters.append(f'report.crossborder = {BooleanExtendedField.to_internal_value(None, cross_border)}')

        if degree_outcome := request.query_params.get('degree_outcome', None):
            if BooleanExtendedField.to_internal_value(None, degree_outcome):
                filters.append(f'degree_outcome = 1')
            else:
                filters.append(f'degree_outcome > 1')

        if programme_type := request.query_params.get('programme_type', None):
            filters.append(f'programme_type = "{programme_type}"')

        if qf_ehea_level := request.query_params.get('qf_ehea_level', None):
            filters.append(f'qf_ehea_level = "{qf_ehea_level}"')

        if valid_on := request.query_params.get('valid_on', False):
            try:
                filters.append(f'report.valid_from <= {int(datetime.datetime.fromisoformat(valid_on).timestamp())}')
                filters.append(f'report.valid_to_calculated >= {int(datetime.datetime.fromisoformat(valid_on).timestamp())}')
            except ValueError:
                raise ParseError(detail=f'value [{valid_on}] for year cannot be parsed to datetime')

        return filters

    def convert_hit(self, p):
        """
        convert result structure
        """

        # date formats
        p['report']['valid_from'] = self.timestamp_to_isodatetime(p['report']['valid_from'])
        p['report']['valid_to_calculated'] = self.timestamp_to_isodatetime(p['report']['valid_to_calculated'])
        p['report']['valid_to'] = self.timestamp_to_isodatetime(p['report']['valid_to'])
        p['report']['created_at'] = self.timestamp_to_isodatetime(p['report']['created_at'])
        p['report']['updated_at'] = self.timestamp_to_isodatetime(p['report']['updated_at'])

        # adjust degree outcome semantics
        p['degree_outcome'] = p['degree_outcome'] == 1

        # make file paths absolute
        for f in p["report"]["report_files"]:
            if "file" in f:
                f["file"] = self.request.build_absolute_uri(f['file'])

        return p


class ReportDetail(generics.RetrieveAPIView):
    """
    Returns the details about a single report
    """
    serializer_class = ReportDetailSerializer
    queryset = Report.objects.all()
