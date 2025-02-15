from django.conf import settings
from django.db.models import Q
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from pysolr import SolrError
from rest_framework import generics, permissions
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from agencies.models import AgencyESGActivity
from connectapi.europass.accrediation_xml_creator_v2 import AccrediationXMLCreatorV2
from countries.models import Country
from eqar_backend.searchers import Searcher
from eqar_backend.xml_renderer import XMLRenderer
from institutions.models import Institution
from adminapi.inspectors.institution_search_inspector import InstitutionSearchInspector
from webapi.v2.serializers.agency_serializers import AgencyActivityDEQARConnectListSerializer
from webapi.v2.serializers.institution_serializers import InstitutionDEQARConnectListSerializer


class InstitutionFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search')
    country = filters.CharFilter(label='Country')
    city = filters.CharFilter(label='City')
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
class InstitutionDEQARConnectList(ListAPIView):
    """
    Returns a list of all the institutions existing in DEQAR.
    """
    queryset = Institution.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = InstitutionFilterClass
    serializer_class = InstitutionDEQARConnectListSerializer
    core = getattr(settings, "SOLR_CORE_INSTITUTIONS", "deqar-institutions")
    permission_classes = (permissions.AllowAny,)

    def list(self, request, *args, **kwargs):
        limit = request.query_params.get('limit', 10)
        offset = request.query_params.get('offset', 0)

        filters = []
        qf = [
            'name_official^5',
            'name_official_transliterated',
            'name_english^2.5',
            'name_version^1.5',
            'name_version_transliterated^1.5',
            'country_search^2.5',
            'city_search^2.5',
            'eter_id^2',
            'deqar_id^2',
        ]
        params = {
            'search': request.query_params.get('query', ''),
            'ordering': request.query_params.get('ordering', '-score'),
            'qf': qf,
            'fl': 'id,eter_id,deqar_id,name_primary,'
                  'website_link,country,city',
            'facet': True,
            'facet_fields': ['country_facet'],
            'facet_sort': 'index'
        }

        country = request.query_params.get('country', None)
        city = request.query_params.get('city', None)
        eter_id = request.query_params.get('eter_id', None)
        deqar_id = request.query_params.get('deqar_id', None)

        if country:
            filters.append({'country': country})
        if city:
            filters.append({'city': city})
        if eter_id:
            filters.append({'eter_id': eter_id})
        if deqar_id:
            filters.append({'deqar_id_search': deqar_id})

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


class AgencyActivityDEQARConnectList(generics.ListAPIView):
    """
    Returns a list of the activities for each Agency where the user has the right to submit.
    """
    serializer_class = AgencyActivityDEQARConnectListSerializer

    def get_queryset(self):
        user = self.request.user
        submitting_agency = user.deqarprofile.submitting_agency.submitting_agency.all()
        return AgencyESGActivity.objects.filter(agency__allowed_agency__in=submitting_agency)\
            .order_by('agency__acronym_primary')


class AccreditationXMLViewV2(APIView):
    permission_classes = []
    renderer_classes = (XMLRenderer,)

    def get(self, request, *args, **kwargs):
        country_code = self.kwargs['country_code']
        country = get_object_or_404(
            Country, Q(iso_3166_alpha3=country_code.upper()) | Q(iso_3166_alpha2__exact=country_code)
        )
        creator = AccrediationXMLCreatorV2(country, request)
        return Response(creator.create(), content_type='application/xml')
