import datetime
import json
import re

from django.utils.decorators import method_decorator

from django_filters import rest_framework as filters, OrderingFilter

from drf_yasg.utils import swagger_auto_schema

from rest_framework.exceptions import ParseError

from webapi.v2.views.meili_solr_view import MeiliSolrBackportView

from adminapi.inspectors.report_search_inspector import ReportSearchInspector
from eqar_backend.serializer_fields.boolean_extended_serializer_field import BooleanExtendedField

from lists.models import Language
from reports.models import  Report, \
                            ReportStatus, \
                            ReportDecision
from agencies.models import Agency, \
                            AgencyESGActivity, \
                            AgencyActivityGroup, \
                            AgencyActivityType
from countries.models import Country


class ReportFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search')
    agency = filters.ModelChoiceFilter(label='Agency',
                queryset=Agency.objects.all(),
                to_field_name='acronym_primary')
    activity_id = filters.ModelChoiceFilter(label='Agency ESG Activity',
                queryset=AgencyESGActivity.objects.all(),
                to_field_name='id')
    activity_group_id = filters.ModelChoiceFilter(label='ESG Activity Group',
                queryset=AgencyActivityGroup.objects.all(),
                to_field_name='id')
    activity_type = filters.ModelChoiceFilter(label='Activity Type',
                queryset=AgencyActivityType.objects.all(),
                to_field_name='type')
    country = filters.ModelChoiceFilter(label='Country',
                queryset=Country.objects.all(),
                to_field_name='name_english')
    status = filters.ModelChoiceFilter(label='Status',
                queryset=ReportStatus.objects.all(),
                to_field_name='status')
    decision = filters.ModelChoiceFilter(label='Decision',
                queryset=ReportDecision.objects.all(),
                to_field_name='decision')
    cross_border = filters.BooleanFilter(label='Cross-border')
    flag = filters.CharFilter(label='Flag')
    language = filters.ModelChoiceFilter(label='Language',
                queryset=Language.objects.all(),
                to_field_name='language_name_en')
    active = filters.BooleanFilter(label='Active')
    year = filters.NumberFilter(label='Year')
    other_provider_covered = filters.BooleanFilter(label='Other Provider Covered')
    degree_outcome = filters.BooleanFilter(label='Degree Outcome')

    ordering = OrderingFilter(
        fields=(
            "institution_programme_sort",
            "agency",
            "country",
            "activity",
            "flag",
            "valid_from",
            "valid_to_calculated",
            "date_created",
            "date_updated",
        )
    )


@method_decorator(name='get', decorator=swagger_auto_schema(
   filter_inspectors=[ReportSearchInspector]
))
class ReportList(MeiliSolrBackportView):
    """
    Returns a list of reports based on Meilisearch

    NB: This is a compatibility with for the legacy v2 view, originally based on Solr. It
    operates on the Meilisearch index and enriches the results to be fully compatible with
    the original v2 return format.
    """
    queryset = Report.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ReportFilterClass

    MEILI_INDEX = 'INDEX_REPORTS'
    ORDERING_MAPPING = {
        "institution_programme_sort": "institutions.name_sort",
        "date_created": "created_at",
        "date_updated": "updated_at",
        "valid_from": "valid_from",
        "valid_to_calculated": "valid_to_calculated",
        "agency": "agency.acronym_primary",
        "country": "institutions.locations.country.name_english",
        "activity": "agency_esg_activities.type",
        "flag": "flag",
    }
    FACET_NAMES = {
        'agency.id': 'agency_facet',
        'contributing_agencies.id': 'agency_facet',
        'institutions.locations.country.id': 'country_facet',
        'platforms.locations.country.id': 'country_facet',
        'flag': 'flag_level_facet',
        'agency_esg_activities.group_id': 'activity_facet',
        'agency_esg_activities.type': 'activity_type_facet',
        'status': 'status_facet',
        'decision': 'decision_facet',
        'report_files.languages': 'language_facet',
        'crossborder': 'crossborder_facet',
        'other_provider_covered': 'other_provider_covered_facet',
        'programmes.degree_outcome': 'degree_outcome_facet',
        'programmes.programme_type': 'programme_type_facet'
    }
    FACET_LOOKUP = {
        'agency.id':                         { 'model': Agency,            'attribute': 'acronym_primary' },
        'contributing_agencies.id':          { 'model': Agency,            'attribute': 'acronym_primary' },
        'institutions.locations.country.id': { 'model': Country,           'attribute': 'name_english' },
        'platforms.locations.country.id':    { 'model': Country,           'attribute': 'name_english' },
        'agency_esg_activities.group_id':    { 'model': AgencyActivityGroup, 'attribute': 'activity' },
    }


    def make_filters(self, request):
        filters = []

        if agency_id := self.lookup_object(Agency, 'acronym_primary', 'agency', 'id', 'agency_id'):
            filters.append(f'agency.id = {agency_id} OR contributing_agencies.id = {agency_id}')

        if activity_ids := self.lookup_object(AgencyESGActivity, 'activity', 'activity', 'id', 'activity_id', multi=True):
            filters.append(f'agency_esg_activities.id IN [ {activity_ids} ]')

        if activity_group_ids := self.lookup_object(AgencyActivityGroup, 'activity', 'activity_group', 'id', 'activity_group_id', multi=True):
            filters.append(f'agency_esg_activities.group_id IN [ {activity_group_ids} ]')

        if activity_type := self.lookup_object(AgencyActivityType, 'id', 'activity_type_id', 'type', 'activity_type'):
            filters.append(f'agency_esg_activities.type = "{activity_type}"')

        if country_id := self.lookup_object(Country, 'name_english', 'country', 'id', 'country_id'):
            filters.append(f'institutions.locations.country.id = {country_id} OR platforms.locations.country.id = {country_id}')

        if status := self.lookup_object(ReportStatus, 'id', 'status_id', 'status', 'status'):
            filters.append(f'status = "{status}"')

        if decision := self.lookup_object(ReportDecision, 'id', 'decision_id', 'decision', 'decision'):
            filters.append(f'decision = "{decision}"')

        if language := self.lookup_object(Language, 'id', 'language_id', 'language_name_en', 'language'):
            filters.append(f'report_files.languages = "{language}"')

        if cross_border := request.query_params.get('cross_border', None):
            filters.append(f'crossborder = {BooleanExtendedField.to_internal_value(None, cross_border)}')

        if other_provider_covered := request.query_params.get('other_provider_covered', None):
            filters.append(f'other_provider_covered = {BooleanExtendedField.to_internal_value(None, other_provider_covered)}')

        if degree_outcome := request.query_params.get('degree_outcome', None):
            if BooleanExtendedField.to_internal_value(None, degree_outcome):
                filters.append(f'programmes.degree_outcome = 1')
            else:
                filters.append(f'programmes.degree_outcome > 1')

        if flag := request.query_params.get('flag', None):
            filters.append(f'flag = "{flag}"')
        else:
            filters.append(f'flag != "high level"')

        if programme_type := request.query_params.get('programme_type', None):
            filters.append(f'programmes.programme_type = "{programme_type}"')

        if active := request.query_params.get('active', False):
            if BooleanExtendedField.to_internal_value(None, active):
                filters.append(f'valid_to_calculated >= {int(datetime.datetime.now().timestamp())}')

        if year := request.query_params.get('year', False):
            try:
                filters.append(f'valid_from <= {int(datetime.datetime(year=int(year), month=12, day=31, hour=23, minute=59, second=59).timestamp())}')
                filters.append(f'valid_to_calculated >= {int(datetime.datetime(year=int(year), month=1, day=1, hour=0, minute=0, second=0).timestamp())}')
            except ValueError:
                raise ParseError(detail=f'value [{year}] for year cannot be parsed to int')

        return filters

    def convert_hit(self, r):
        """
        convert result structure
        """
        # compatibility
        if r['local_identifier']:
            r['local_id'] = [ r['local_identifier'] ]
        r["flag_level"] = r.pop("flag")

        # date formats
        r['valid_from'] = self.timestamp_to_isodatetime(r['valid_from'])
        r['valid_to_calculated'] = self.timestamp_to_isodatetime(r['valid_to_calculated'])
        r['valid_to'] = self.timestamp_to_isodatetime(r['valid_to'])
        r['date_created'] = self.timestamp_to_isodatetime(r.pop('created_at'))
        r['date_updated'] = self.timestamp_to_isodatetime(r.pop('updated_at'))

        # additional agency and activity info
        agency = Agency.objects.get(id=r['agency']['id'])
        r['agency_name'] = agency.name_primary
        r['agency_acronym'] = r['agency']['acronym_primary']

        # Temporary fix, to prevent frontend from crashing
        if len(r['agency_esg_activities']) > 0:
            activity = AgencyESGActivity.objects.get(id=r['agency_esg_activities'][0]['id'])
            r['agency_esg_activity'] = activity.activity_group.activity
            r['agency_esg_activity_type'] = r['agency_esg_activities'][0]['type']
        else:
            r['agency_esg_activity'] = 'N/A'
            r['agency_esg_activity_type'] = 'N/A'

        # reformat contributing agency list
        for ca in r['contributing_agencies']:
            contributing_agency = Agency.objects.get(id=ca['id'])
            ca['agency_id'] = ca.pop('id')
            ca['agency_acronym'] = ca.pop('acronym_primary')
            ca['agency_name'] = contributing_agency.name_primary
            ca['agency_url'] = contributing_agency.website_link

        # adjust degree outcome semantics
        for p in r['programmes']:
            p['degree_outcome'] = p['degree_outcome'] == 1

        # merged country list
        countries = set()
        for i in r['institutions']:
            for l in i['locations']:
                countries.add(l['country']['name_english'])
        r["country"] = list(countries)

        # make file paths absolute
        for f in r["report_files"]:
            if "file" in f:
                f["file"] = self.request.build_absolute_uri(f['file'])

