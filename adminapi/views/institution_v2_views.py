from django.conf import settings
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from eqar_backend.searchers import Searcher
from institutions.models import Institution
from webapi.inspectors.institution_search_inspector import InstitutionSearchInspector


class InstitutionFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search')

    ordering = OrderingFilter(
        fields=(
            ('score', 'score'),
            ('name', 'name_sort')
        )
    )


@method_decorator(name='get', decorator=swagger_auto_schema(
   filter_inspectors=[InstitutionSearchInspector],
))
class InstitutionAllList(ListAPIView):
    """
    Returns a list of all the institutions to which report was submitted in DEQAR.
    """
    queryset = Institution.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = InstitutionFilterClass
    core = getattr(settings, "SOLR_CORE_INSTITUTION_ALL", "deqar-institutions-all")

    def list(self, request, *args, **kwargs):
        limit = request.query_params.get('limit', 10)
        offset = request.query_params.get('offset', 0)

        filters = []
        qf = [
            'name_official^2.5',
            'name_official_transliterated',
            'name_english^2.5',
            'name_version^1.5',
            'name_version_transliterated^1.5',
            'country^1.5',
            'city^2',
            'eter_id^2'
        ]
        params = {
            'search': request.query_params.get('query', ''),
            'ordering': request.query_params.get('ordering', '-score'),
            'qf': qf,
            'fl': 'id,eter_id,name_primary,name_select_display,name_sort,place,website_link,score'
        }

        country = request.query_params.get('country', None)
        if country:
            filters.append({'country': country})
        params['filters'] = filters

        searcher = Searcher(self.core)
        searcher.initialize(params, start=offset, rows_per_page=limit, tie_breaker='name_sort asc')
        response = searcher.search()
        resp = {
            'count': response.hits,
            'results': response.docs,
        }
        if (int(limit) + int(offset)) < int(response.hits):
            resp['next'] = True
        return Response(resp)
