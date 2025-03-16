import datetime
import json
import re

from collections import defaultdict

from rest_framework.exceptions import ParseError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from eqar_backend.meilisearch import MeiliClient
from meilisearch.errors import MeilisearchApiError


class MeiliSolrBackportView(ListAPIView):
    """
    A compatibility view for the legacy v2 API, originally based on Solr. The class helps
    create views that operate on the Meilisearch index and enrich the results to be fully
    compatible with the original v2 return format.

    This class is meant to be sub-classed. In the sub-class, set the usual properties for ListAPIView plus:

     - MEILI_INDEX (string) : name of the Meilisearch index to use
     - ORDERING_MAPPING (dict) : maps old (Solr) ordering parameter values to the ones used for Meili
     - FACET_NAMES (dict) : maps the name of Meili facets to old (Solr) ones for the API response
     - FACET_LOOKUP (dict of dicts) : specifies which (numeric) facet values have to be looked up in DB,
                     member dicts of the format { 'model': Model, 'attribute': 'attribute to return' }
    """

    def zero_or_more(self, request, field, default):
        """
        get numeric paramater that should be greater or equal 0
        """
        value = request.query_params.get(field, default)
        if value == '':
            value = default
        if not str(value).isdecimal():
            raise ParseError(detail='%s should be zero or larger number.' % field)
        return int(value)


    def timestamp_to_isodate(self, timestamp):
        """
        convert Unix timestamp to ISO format date
        """
        return datetime.date.fromtimestamp(timestamp).isoformat() if timestamp is not None else None


    def timestamp_to_isodatetime(self, timestamp):
        """
        convert Unix timestamp to ISO format date and time
        """
        return datetime.datetime.fromtimestamp(timestamp).isoformat() + "Z" if timestamp is not None else None


    def convert_ordering(self, ordering):
        """
        map legacy ordering parameters to Meilisearch ones
        """
        if ordering in [ "score", "-score", "" ]:
            return None
        elif ordering[0:1] == '-':
            field = ordering[1:]
            direction = 'desc'
        else:
            field = ordering
            direction = 'asc'
        if field in self.ORDERING_MAPPING:
            return [ f'{self.ORDERING_MAPPING[field]}:{direction}' ]
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


    def make_filters(self, request):
        """
        Overwrite this function and create filters from request parameters

        request : DRF request object - return : list
        """
        raise NotImplemented


    def make_meili_params(self, request):
        """
        Optionally overwrite this function to add additional Meilisearch parameters

        request : DRF request object - return : dict
        """
        return {}


    def convert_hit(self, hit):
        """
        Convert a single Meilisearch hit to the format of the old Solr-based API

        hit : dict - return : dict
        """
        raise NotImplemented


    def list(self, request, *args, **kwargs):
        """
        The main view function
        """
        self.request = request

        limit = self.zero_or_more(request, 'limit', 10)
        offset = self.zero_or_more(request, 'offset', 0)

        meili = MeiliClient()
        index = getattr(meili, self.MEILI_INDEX)

        params = {
            'sort': self.convert_ordering(request.query_params.get('ordering', '-score')),
            'filter': self.make_filters(request),
            'facets': list(self.FACET_NAMES.keys()),
            'hitsPerPage': limit,
            'page': int(offset/limit) + 1 if limit > 0 else 1,
            **self.make_meili_params(request),
        }

        try:
            response = meili.meili.index(index).search(query=request.query_params.get('query', ''), opt_params=params)
        except MeilisearchApiError as e:
            return Response(status=HTTP_400_BAD_REQUEST, data={'error': str(e)})

        # convert result structure
        for r in response['hits']:
            self.convert_hit(r)

        # rename, lookup and merge
        fields = defaultdict(lambda: defaultdict(int))
        for facet_name, distribution in response['facetDistribution'].items():
            for value, count in distribution.items():
                if facet_name in self.FACET_LOOKUP:
                    try:
                        obj = self.FACET_LOOKUP[facet_name]['model'].objects.get(id=value)
                        fields[self.FACET_NAMES[facet_name]][getattr(obj, self.FACET_LOOKUP[facet_name]['attribute'])] += count
                    except self.FACET_LOOKUP[facet_name]['model'].DoesNotExist:
                        fields[self.FACET_NAMES[facet_name]][f'unknown ID: {value}'] += count
                else:
                    fields[self.FACET_NAMES[facet_name]][value] += count
        # restructure in Solr way
        solr_fields = {}
        for facet_name, field in fields.items():
            solr_fields[facet_name] = [item for pair in field.items() for item in pair]

        # create a response dict looking like the Solr one
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
