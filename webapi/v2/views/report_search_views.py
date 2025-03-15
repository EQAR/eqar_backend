import datetime
import json
import re

from collections import defaultdict

from django.conf import settings
from django.utils.decorators import method_decorator

from django_filters import rest_framework as filters, OrderingFilter

from drf_yasg.utils import swagger_auto_schema

from rest_framework.exceptions import ParseError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from eqar_backend.meilisearch import MeiliClient
from meilisearch.errors import MeilisearchApiError

from adminapi.inspectors.report_search_inspector import ReportSearchInspector
from eqar_backend.serializer_fields.boolean_extended_serializer_field import BooleanExtendedField

from lists.models import Language
from reports.models import Report, ReportStatus, ReportDecision
from agencies.models import Agency, AgencyESGActivity, AgencyActivityType
from countries.models import Country

class ReportFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search')
    agency = filters.ModelChoiceFilter(label='Agency',
                queryset=Agency.objects.all(),
                to_field_name='acronym_primary')
    activity = filters.ModelChoiceFilter(label='Agency ESG Activity',
                queryset=AgencyESGActivity.objects.all(),
                to_field_name='activity')
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
class ReportList(ListAPIView):
    """
    Returns a list of reports based on Meilisearch

    NB: This is a compatibility with for the legacy v2 view, originally based on Solr. It
    operates on the Meilisearch index and enriches the results to be fully compatible with
    the original v2 return format.
    """
    queryset = Report.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ReportFilterClass

    def zero_or_more(self, request, field, default):
        value = request.query_params.get(field, default)
        if value == '':
            value = default
        if not str(value).isdecimal():
            raise ParseError(detail='%s should be zero or larger number.' % field)
        return int(value)


    def convert_ordering(self, ordering):
        """
        map legacy ordering parameters to Meilisearch ones
        """
        MAPPING = {
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
        if ordering in [ "score", "-score", "" ]:
            return None
        elif ordering[0:1] == '-':
            field =ordering[1:]
            direction = 'desc'
        else:
            field = ordering
            direction = 'asc'
        if field in MAPPING:
            return [ f'{MAPPING[field]}:{direction}' ]
        else:
            raise ParseError(detail=f'unknown field [{field}] for ordering')


    def lookup_object(self, model, key, parameter, attribute, raw_parameter, multi=False):
        """
        If parameter is set, looks up model object against key and returns its attribute - otherwise raw_parameter if set
        """
        if lookup := self.request.query_params.get(parameter, None):
            if multi:
                obj = model.objects.filter(**{key: lookup})
                if obj.count() == 0:
                    raise ParseError(detail=f'unknown value [{lookup}] for {parameter}')
                else:
                    return ', '.join([ str(getattr(i, attribute)) for i in obj ])
            else:
                try:
                    obj = model.objects.get(**{key: lookup})
                    return getattr(obj, attribute)
                except model.DoesNotExist:
                    raise ParseError(detail=f'unknown value [{lookup}] for {parameter}')
        else:
            return self.request.query_params.get(raw_parameter, None)


    def list(self, request, *args, **kwargs):
        self.request = request

        limit = self.zero_or_more(request, 'limit', 10)
        offset = self.zero_or_more(request, 'offset', 0)

        filters = []

        if agency_id := self.lookup_object(Agency, 'acronym_primary', 'agency', 'id', 'agency_id'):
            filters.append(f'agency.id = {agency_id} OR contributing_agencies.id = {agency_id}')

        if activity_ids := self.lookup_object(AgencyESGActivity, 'activity', 'activity', 'id', 'activity_id', multi=True):
            filters.append(f'agency_esg_activities.id IN [ {activity_ids} ]')

        if activity_type := self.lookup_object(AgencyActivityType, 'id', 'activity_type_id', 'type', 'activity_type'):
            filters.append(f'agency_esg_activities.type = "{activity_type}"')

        if country_id := self.lookup_object(Country, 'name_english', 'country', 'id', 'country_id'):
            filters.append(f'institutions.locations.country.id = {country_id}')

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

        meili = MeiliClient()
        params = {
            'sort': self.convert_ordering(request.query_params.get('ordering', '-score')),
            'filter': filters,
            'facets': [
                'agency.id',
                'agency_esg_activities.id',
                'agency_esg_activities.type',
                'contributing_agencies.id',
                'crossborder',
                'decision',
                'flag',
                'institutions.locations.country.id',
                'other_provider_covered',
                'programmes.degree_outcome',
                'programmes.programme_type',
                'report_files.languages',
                'status',
            ],
            'hitsPerPage': limit,
            'page': int(offset/limit) + 1 if limit > 0 else 1,
        }

        try:
            response = meili.meili.index(meili.INDEX_REPORTS).search(query=request.query_params.get('query', ''), opt_params=params)
        except MeilisearchApiError as e:
            return Response(status=HTTP_400_BAD_REQUEST, data={'error': str(e)})

        # convert result structure
        for r in response['hits']:
            # compatibility
            if r['local_identifier']:
                r['local_id'] = [ r['local_identifier'] ]
            r["flag_level"] = r.pop("flag")

            # date formats
            r['valid_from'] = datetime.datetime.fromtimestamp(r['valid_from']).isoformat() + "Z"
            r['valid_to_calculated'] = datetime.datetime.fromtimestamp(r['valid_to_calculated']).isoformat() + "Z"
            if r['valid_to']:
                r['valid_to'] = datetime.datetime.fromtimestamp(r['valid_to']).isoformat() + "Z"
            r['date_created'] = datetime.datetime.fromtimestamp(r.pop('created_at')).isoformat() + "Z"
            r['date_updated'] = datetime.datetime.fromtimestamp(r.pop('updated_at')).isoformat() + "Z"

            # additional agency and activity info
            agency = Agency.objects.get(id=r['agency']['id'])
            activity = AgencyESGActivity.objects.get(id=r['agency_esg_activities'][0]['id'])
            r['agency_name']= agency.name_primary
            r['agency_acronym'] = r['agency']['acronym_primary']
            r['agency_esg_activity'] = activity.activity
            r['agency_esg_activity_type'] = r['agency_esg_activities'][0]['type']

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

        # convert facets
        FACET_NAMES = {
            'agency.id': 'agency_facet',
            'contributing_agencies.id': 'agency_facet',
            'institutions.locations.country.id': 'country_facet',
            'flag': 'flag_level_facet',
            'agency_esg_activities.id': 'activity_facet',
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
            'institutions.locations.country.id': { 'model': Country,           'attribute': 'name_english' },
            'agency_esg_activities.id':          { 'model': AgencyESGActivity, 'attribute': 'activity' },
        }
        # rename, lookup and merge
        fields = defaultdict(lambda: defaultdict(int))
        for facet_name, distribution in response['facetDistribution'].items():
            for value, count in distribution.items():
                if facet_name in FACET_LOOKUP:
                    try:
                        obj = FACET_LOOKUP[facet_name]['model'].objects.get(id=value)
                        fields[FACET_NAMES[facet_name]][getattr(obj, FACET_LOOKUP[facet_name]['attribute'])] += count
                    except FACET_LOOKUP[facet_name]['model'].DoesNotExist:
                        fields[FACET_NAMES[facet_name]][f'unknown ID: {value}'] += count
                else:
                    fields[FACET_NAMES[facet_name]][value] += count
        # restructure for Solr
        solr_fields = {}
        for facet_name, field in fields.items():
            solr_fields[facet_name] = [item for pair in field.items() for item in pair]

        resp = {
            'count': response['totalHits'],
            'next': (limit + offset < response['totalHits']),
            'results': response['hits'],
            'facets': {
                'facet_queries': {},
                'facet_fields': solr_fields,
                'facet_ranges': {},
                'facet_intervals': {},
                'facet_heatmaps': {},
            },
        }

        return Response(resp)
