from django.conf import settings
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from pysolr import SolrError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from eqar_backend.searchers import Searcher
from institutions.models import Institution
from adminapi.inspectors.institution_search_inspector import InstitutionSearchInspector


class InstitutionFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search')
    country = filters.CharFilter(label='Country')
    city = filters.CharFilter(label='City')
    other_provider = filters.BooleanFilter(label='Other Provider')
    eter_id = filters.CharFilter(label='ETER ID')
    deqar_id = filters.CharFilter(label='DEQAR ID')

    ordering = OrderingFilter(
        fields=(
            ('score', 'score'),
            ('name_primary', 'name_sort'),
            ('deqar_id', 'deqar_id_sort'),
            ('eter_id', 'eter_id_sort')
        )
    )


@method_decorator(name='get', decorator=swagger_auto_schema(
   filter_inspectors=[InstitutionSearchInspector],
))
class InstitutionAllList(ListAPIView):
    """
    Returns a list of all the institutions existing in DEQAR.
    """
    queryset = Institution.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = InstitutionFilterClass
    core = getattr(settings, "SOLR_CORE_INSTITUTIONS", "deqar-institutions")

    def list(self, request, *args, **kwargs):
        limit = request.query_params.get('limit', 10)
        offset = request.query_params.get('offset', 0)

        filters = []
        qf = [
            'name_official^5',
            'acronym_search^5',
            'name_official_transliterated',
            'name_english^2.5',
            'name_version^1.5',
            'name_version_transliterated^1.5',
            'country^2.5',
            'city^2.5',
            'eter_id^2',
            'deqar_id^2',
        ]
        params = {
            'search': request.query_params.get('query', ''),
            'ordering': request.query_params.get('ordering', '-score'),
            'qf': qf,
            'fl': 'id,eter_id,deqar_id,name_primary,name_display,name_select_display,name_sort,place,'
                  'website_link,country,city,other_provider,score',
            'facet': True,
            'facet_fields': ['country_facet'],
            'facet_sort': 'index'
        }

        country = request.query_params.get('country', None)
        city = request.query_params.get('city', None)
        eter_id = request.query_params.get('eter_id', None)
        deqar_id = request.query_params.get('deqar_id', None)
        other_provider = request.query_params.get('other_provider', None)

        if country:
            filters.append({'country': country})
        if city:
            filters.append({'city': city})
        if eter_id:
            filters.append({'eter_id': eter_id})
        if deqar_id:
            filters.append({'deqar_id_search': deqar_id})
        if other_provider:
            filters.append({'other_provider_facet': other_provider})

        params['filters'] = filters

        searcher = Searcher(self.core)
        searcher.initialize(params, start=offset, rows_per_page=limit, tie_breaker='name_sort asc')

        try:
            response = searcher.search()
        except SolrError as e:
            return Response(status=HTTP_400_BAD_REQUEST, data={'error': str(e)})

        resp = {
            'count': response.hits,
            'results': response.docs,
            'facets': response.facets
        }
        if (int(limit) + int(offset)) < int(response.hits):
            resp['next'] = True
        return Response(resp)
