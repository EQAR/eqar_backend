import json
import datetime

from collections import defaultdict

from django.conf import settings
from django.http import Http404
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from pysolr import SolrError
from rest_framework import generics
from rest_framework.exceptions import ParseError, APIException
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from eqar_backend.meilisearch import MeiliClient
from meilisearch.errors import MeilisearchApiError

from agencies.models import Agency, AgencyESGActivity, AgencyActivityType
from countries.models import Country
from eqar_backend.searchers import Searcher
from institutions.models import Institution, InstitutionIdentifier
from lists.models import QFEHEALevel, IdentifierResource
from reports.models import ReportStatus
from webapi.inspectors.institution_search_inspector import InstitutionSearchInspector
from webapi.v2.serializers.institution_serializers import InstitutionResourceSerializer, InstitutionDetailSerializer


class InstitutionFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search')
    country = filters.ModelChoiceFilter(label='Country', queryset=Country.objects.all(),
                                        to_field_name='name_english')
    country_id = filters.ModelChoiceFilter(label='Country ID', queryset=Country.objects.all(),
                                           to_field_name='id')
    agency = filters.ModelChoiceFilter(label='Agency', queryset=Agency.objects.all(),
                                       to_field_name='acronym_primary')
    agency_id = filters.ModelChoiceFilter(label='Agency ID', queryset=Agency.objects.all(),
                                          to_field_name='id')
    activity = filters.ModelChoiceFilter(label='Activity', queryset=AgencyESGActivity.objects.all(),
                                         to_field_name='activity_display')
    activity_id = filters.ModelChoiceFilter(label='Activity ID', queryset=AgencyESGActivity.objects.all(),
                                            to_field_name='id')
    activity_type = filters.ModelChoiceFilter(label='Activity Type', queryset=AgencyActivityType.objects.all(),
                                              to_field_name='type')
    activity_type_id = filters.ModelChoiceFilter(label='Activity Type ID', queryset=AgencyActivityType.objects.all(),
                                                 to_field_name='id')
    status = filters.ModelChoiceFilter(label='Report Status', queryset=ReportStatus.objects.all(),
                                       to_field_name='status')
    status_id = filters.ModelChoiceFilter(label='Report Status ID', queryset=ReportStatus.objects.all(),
                                          to_field_name='id')
    qf_ehea_level = filters.ModelChoiceFilter(label='QF EHEA Level', queryset=QFEHEALevel.objects.all(),
                                              to_field_name='level')
    qf_ehea_level_id = filters.ModelChoiceFilter(label='QF EHEA Level ID', queryset=QFEHEALevel.objects.all(),
                                                 to_field_name='id')
    crossborder = filters.BooleanFilter(label='Crossborder')
    other_provider = filters.BooleanFilter(label='Other Provider')

    ordering = OrderingFilter(
        fields=(
            'score',
            'name_sort',
            'founding_date',
            'closure_date',
            'country'
        )
    )


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[InstitutionSearchInspector]
))
class InstitutionList(ListAPIView):
    """
    Returns a list of all the institutions to which a report was submitted in DEQAR

    NB: This is a compatibility with for the legacy v2 view, originally based on Solr. It
    operates on the Meilisearch index and enriches the results to be fully compatible with
    the original v2 return format.
    """
    queryset = Institution.objects.all()
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = InstitutionFilterClass

    def zero_or_more(self, request, field, default):
        value = request.query_params.get(field, default)
        if not str(value).isdigit():
            raise ParseError(detail='%s should be zero or larger number.' % field)
        value = default if value == '' else value
        return value


    def convert_ordering(self, ordering):
        """
        map legacy ordering parameters to Meilisearch ones
        """
        MAPPING = {
            'name_sort': 'name_sort',
            'founding_date': 'founding_date',
            'closure_date': 'closure_date',
            'country': 'locations.country.name_english',
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

        # this view shows only institutions with reports
        filters = [ 'has_report = True' ]

        if country_id := self.lookup_object(Country, 'name_english', 'country', 'id', 'country_id'):
            filters.append(f'locations.country.id = {country_id}')

        if request.query_params.get('activity', None) or request.query_params.get('activity_id', None):
            raise ParseError(detail='filtering by activity name or ID is no longer supported by the Web API')

        if agency_id := self.lookup_object(Agency, 'acronym_primary', 'agency', 'id', 'agency_id'):
            filters.append(f'agencies.id = {agency_id}')

        if status := self.lookup_object(ReportStatus, 'id', 'status_id', 'status', 'status'):
            filters.append(f'status = "{status}"')

        if qf_ehea_level := self.lookup_object(QFEHEALevel, 'id', 'qf_ehea_level_id', 'level', 'qf_ehea_level'):
            filters.append(f'qf_ehea_levels = "{qf_ehea_level}"')

        if crossborder := request.query_params.get('crossborder', None):
            filters.append(f'crossborder = {BooleanExtendedField.to_internal_value(None, crossborder)}')

        if other_provider := request.query_params.get('other_provider', None):
            filters.append(f'is_other_provider = {BooleanExtendedField.to_internal_value(None, other_provider)}')

        meili = MeiliClient()
        params = {
            'sort': self.convert_ordering(request.query_params.get('ordering', '-score')),
            'filter': filters,
            'facets': [
                'locations.country.id',
                'qf_ehea_levels',
                'agencies.id',
                'status',
                'activity_types',
                'crossborder',
                'is_other_provider',
            ],
            'hitsPerPage': limit,
            'page': int(offset/limit) + 1 if limit > 0 else 1,
        }

        try:
            response = meili.meili.index(meili.INDEX_INSTITUTIONS).search(query=request.query_params.get('query', ''), opt_params=params)
        except MeilisearchApiError as e:
            return Response(status=HTTP_400_BAD_REQUEST, data={'error': str(e)})

        # convert result structure for compatibility
        for r in response['hits']:
            # names
            if r['eter_id']:
                r['name_select_display'] = f"{r['name_primary']} ({r['eter_id']})"
            else:
                r['name_select_display'] = r['name_primary']
            for name in r['names']:
                if name['name_valid_to'] is None:
                    r['name_official_display'] = name['name_official']
                    break
            if r['name_official_display'] != r['name_primary']:
                r['name_display'] = f"{r['name_official_display']} / {r['name_primary']}"
            else:
                r['name_display'] = r['name_primary']

            # QF-EHEA levels
            r['qf_ehea_level'] = r.pop("qf_ehea_levels")

            # relationships
            def convert_related(new_style):
                for rel in new_style:
                    yield {
                        "deqar_id": rel['institution']['deqar_id'],
                        "eter_id": rel['institution']['eter_id'],
                        "name_primary": rel['institution']['name_primary'],
                        "website_link": rel['institution']['website_link'],
                        "relationship_type": rel['relationship_type'],
                        "valid_from": datetime.date.fromtimestamp(rel['valid_from']).isoformat() if rel['valid_from'] else None,
                        "valid_to": datetime.date.fromtimestamp(rel['valid_to']).isoformat() if rel['valid_to'] else None,
                    }
            r['hierarchical_relationships'] = {
                "part_of":  list(convert_related(r.pop("part_of"))),
                "includes": list(convert_related(r.pop("includes"))),
            }

            # date formats
            r['founding_date'] = datetime.date.fromtimestamp(r['founding_date']).isoformat() if r['founding_date'] else None
            r['closure_date'] = datetime.date.fromtimestamp(r['closure_date']).isoformat() if r['closure_date'] else None
            r['date_created'] = datetime.datetime.fromtimestamp(r.pop('created_at')).isoformat() + "Z"

            # merged country list
            countries = set()
            for l in r['locations']:
                countries.add(l['country']['name_english'])
            r["country"] = list(countries)

            # location
            r['place'] = r.pop("locations")
            for loc in r['place']:
                loc["country"] = loc['country']['name_english']
                loc["country_valid_from"] = datetime.date.fromtimestamp(loc['country_valid_from']).isoformat() if loc['country_valid_from'] else None
                loc["country_valid_to"] = datetime.date.fromtimestamp(loc['country_valid_to']).isoformat() if loc['country_valid_to'] else None


        # convert facets
        FACET_NAMES = {
            'locations.country.id': 'country_facet',
            'qf_ehea_levels': 'qf_ehea_level_facet',
            'agencies.id': 'reports_agencies',
            'status': 'status_facet',
            'activity_types': 'activity_type_facet',
            'crossborder': 'crossborder_facet',
            'is_other_provider': 'other_provider_facet',
        }
        FACET_LOOKUP = {
            'agencies.id':          { 'model': Agency,            'attribute': 'acronym_primary' },
            'locations.country.id': { 'model': Country,           'attribute': 'name_english' },
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


class InstitutionDetailByETER(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected institution (via ETER).
    """
    serializer_class = InstitutionDetailSerializer

    def get_object(self):
        try:
            return Institution.objects.get(eter_id=self.kwargs['eter_id'])
        except Institution.DoesNotExist:
            raise Http404


class InstitutionDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected institution.
    """
    serializer_class = InstitutionDetailSerializer

    def get_queryset(self):
        qs = Institution.objects.filter(pk=self.kwargs['pk'])
        return qs


class InstitutionDetailByIdentifier(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected institution (via identifier).
    """
    serializer_class = InstitutionDetailSerializer

    def get_object(self):
        resource = self.kwargs.get('resource', None)
        identifier = self.kwargs.get('identifier', None)

        try:
            iid = InstitutionIdentifier.objects.filter(identifier=identifier, resource=resource)
            if iid:
                return iid.first().institution
            else:
                raise Http404
        except Institution.DoesNotExist:
            raise Http404


class InstitutionIdentifierResourcesList(generics.ListAPIView):
    """
        Returns all the identifier resources.
    """
    queryset = IdentifierResource.objects.filter(institutionidentifier__isnull=False).distinct()
    serializer_class = InstitutionResourceSerializer
    pagination_class = None
    ordering_fields = ('resource',)
    ordering = ('resource',)
