import json

from django.conf import settings
from django.http import Http404
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from pysolr import SolrError
from rest_framework import generics
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from agencies.models import Agency, AgencyESGActivity, AgencyActivityType
from countries.models import Country
from eqar_backend.searchers import Searcher
from institutions.models import Institution, InstitutionIdentifier
from lists.models import QFEHEALevel
from reports.models import ReportStatus
from webapi.inspectors.institution_search_inspector import InstitutionSearchInspector
from webapi.serializers.institution_serializers import InstitutionDetailSerializer


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
    alternative_provider = filters.BooleanFilter(label='Alternative Provider')

    ordering = OrderingFilter(
        fields=(
            ('score', 'score'),
            ('name', 'name_sort')
        )
    )


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[InstitutionSearchInspector]
))
class InstitutionList(ListAPIView):
    """
    Returns a list of all the institutions to which report was submitted in DEQAR.
    """
    queryset = Institution.objects.all()
    filter_backends = (filters.DjangoFilterBackend, )
    filter_class = InstitutionFilterClass
    core = getattr(settings, "SOLR_CORE_INSTITUTIONS", "deqar-institutions")

    def zero_or_more(self, request, field, default):
        value = request.query_params.get(field, default)
        if not str(value).isdigit():
            raise ParseError(detail='%s should be zero or larger number.' % field)
        value = default if value == '' else value
        return value

    def list(self, request, *args, **kwargs):
        limit = self.zero_or_more(request, 'limit', 10)
        offset = self.zero_or_more(request, 'offset', 0)

        filters = [{'has_report': 'true'}]
        qf = [
            'name_official^2.5',
            'acronym_search^5',
            'name_official_transliterated',
            'name_english^2.5',
            'name_version^1.5',
            'name_version_transliterated^1.5',
            'country^1.5',
            'city^2',
            'aggregated_name_english',
            'aggregated_name_official',
            'aggregated_name_official_transliterated',
            'aggregated_country',
            'aggregated_city'
        ]
        params = {
            'search': request.query_params.get('query', ''),
            'ordering': request.query_params.get('ordering', '-score'),
            'qf': qf,
            'fl': 'id,eter_id,deqar_id,name_primary,name_display,name_official_display,name_select_display,name_sort,'
                  'qf_ehea_level,place,website_link,founding_date,closure_date,hierarchical_relationships,country,'
                  'alternative_provider,score',
            'facet': True,
            'facet_fields': ['country_facet', 'qf_ehea_level_facet', 'reports_agencies', 'status_facet',
                             'activity_facet', 'activity_type_facet', 'crossborder_facet', 'alternative_provider_facet'],
            'facet_sort': 'index'
        }

        eter_id = request.query_params.get('eter_id', None)
        deqar_id = request.query_params.get('deqar_id', None)

        country = request.query_params.get('country', None)
        country_id = request.query_params.get('country_id', None)

        activity = request.query_params.get('activity', None)
        activity_id = request.query_params.get('activity_id', None)

        activity_type = request.query_params.get('activity_type', None)
        activity_type_id = request.query_params.get('activity_type_id', None)

        agency = request.query_params.get('agency', None)
        agency_id = request.query_params.get('agency_id', None)

        status = request.query_params.get('status', None)
        status_id = request.query_params.get('status_id', None)

        qf_ehea_level = request.query_params.get('qf_ehea_level', None)
        qf_ehea_level_id = request.query_params.get('qf_ehea_level_id', None)

        crossborder = request.query_params.get('crossborder', None)
        alternative_provider = request.query_params.get('alternative_provider', None)

        if agency:
            filters.append({'reports_agencies': agency})
        if agency_id:
            filters.append({'agency_id': agency_id})

        if country:
            filters.append({'country_facet': country})
        if country_id:
            filters.append({'country_id': country_id})

        if activity:
            filters.append({'activity_facet': activity})
        if activity_id:
            filters.append({'activity_id': activity_id})

        if activity_type:
            filters.append({'activity_type_facet': activity_type})
        if activity_type_id:
            filters.append({'activity_type_id': activity_type_id})

        if status:
            filters.append({'status_facet': status})
        if status_id:
            filters.append({'status_id': status_id})

        if qf_ehea_level:
            filters.append({'qf_ehea_level': qf_ehea_level})
        if qf_ehea_level_id:
            filters.append({'qf_ehea_level_id': qf_ehea_level_id})

        if eter_id:
            filters.append({'eter_id': eter_id})
        if deqar_id:
            filters.append({'id': deqar_id})

        if crossborder:
            filters.append({'crossborder_facet': crossborder})

        if alternative_provider:
            filters.append({'alternative_provider_facet': alternative_provider})

        params['filters'] = filters

        searcher = Searcher(self.core)
        searcher.initialize(params, start=offset, rows_per_page=limit, tie_breaker='name_sort asc')

        try:
            response = searcher.search()
        except SolrError as e:
            return Response(status=HTTP_400_BAD_REQUEST, data={'error': str(e)})

        for r in response:
            r.update((k, json.loads(v)) for k, v in r.items() if k == 'place')
            r.update((k, json.loads(v)) for k, v in r.items() if k == 'hierarchical_relationships')

        resp = {
            'count': response.hits,
            'results': response.docs,
            'facets': response.facets
        }
        if (int(limit) + int(offset)) < int(response.hits):
            resp['next'] = True
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


class InstitutionIdentifierResourcesList(APIView):
    """
        Returns all the identifier resources.
    """

    @swagger_auto_schema(operation_description="blabla", responses={200: '[list of available resources]'})
    def get(self, request):
        ids = []
        for identifier in InstitutionIdentifier.objects.values('resource').distinct().iterator():
            ids.append(identifier['resource'])
        return Response(sorted(ids, key=str.lower))
