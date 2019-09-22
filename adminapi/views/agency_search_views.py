import datetime
import re

from django.conf import settings
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from agencies.models import Agency
from eqar_backend.searchers import Searcher
from webapi.inspectors.institution_search_inspector import InstitutionSearchInspector


class AgencyFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search')

    ordering = OrderingFilter(
        fields=(
            ('score', 'score'),
            ('deqar_id', 'deqar_id_sort'),
            ('acronym', 'acronym_sort'),
            ('name', 'name_sort')
        )
    )


@method_decorator(name='get', decorator=swagger_auto_schema(
   filter_inspectors=[InstitutionSearchInspector],
))
class AgencyList(ListAPIView):
    """
    Returns a list of all the agencies.
    """
    queryset = Agency.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AgencyFilterClass
    core = getattr(settings, "SOLR_CORE_AGENCIES", "deqar-agencies")

    def list(self, request, request_type, *args, **kwargs):
        limit = request.query_params.get('limit', 10)
        offset = request.query_params.get('offset', 0)

        filters = []
        filters_or = []
        date_filters = []

        if request_type == 'my':
            userprofile = request.user.deqarprofile
            submitting_agency = userprofile.submitting_agency
            for agency_proxy in submitting_agency.submitting_agency.all():
                filters_or.append({'id': agency_proxy.allowed_agency.id})

        qf = [
            'name_search^5',
            'acronym_search^5',
            'name_version_search^2.5',
            'acronym_version_search^2.5',
        ]
        params = {
            'search': request.query_params.get('query', ''),
            'ordering': request.query_params.get('ordering', '-score'),
            'qf': qf,
            'fl': 'id,deqar_id,name,acronym,country,valid_from,valid_to,score',
            'facet': True,
            'facet_fields': ['country_facet', 'focus_country_facet'],
            'facet_sort': 'index'
        }

        country = request.query_params.get('country', None)
        focus_country = request.query_params.get('focus_country', None)
        year = request.query_params.get('year', False)
        active = request.query_params.get('active', False)

        if active:
            if active == 'true':
                now = datetime.datetime.now().replace(microsecond=0).isoformat()
                date_filters.append({'valid_to': '[%sZ TO *]' % now})
        if year:
            try:
                if re.match(r'.*([1-3][0-9]{3})', year):
                    date_from = datetime.datetime(year=int(year), month=12, day=31, hour=23, minute=59, second=59).isoformat()
                    date_filters.append({'valid_from': '[* TO %sZ]' % date_from})
                    date_to = datetime.datetime(year=int(year), month=1, day=1, hour=0, minute=0, second=0).isoformat()
                    date_filters.append({'valid_to': '[%sZ TO *]' % date_to})
            except ValueError:
                pass

        if country:
            filters.append({'country_facet': country})
        if focus_country:
            filters.append({'focus_country_facet': focus_country})

        params['filters'] = filters
        params['filters_or'] = filters_or
        params['date_filters'] = date_filters

        searcher = Searcher(self.core)
        searcher.initialize(params, start=offset, rows_per_page=limit, tie_breaker='name_sort asc')
        response = searcher.search()
        resp = {
            'count': response.hits,
            'results': response.docs,
            'facets': response.facets
        }
        if (int(limit) + int(offset)) < int(response.hits):
            resp['next'] = True
        return Response(resp)
