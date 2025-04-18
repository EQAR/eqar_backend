import datetime
import re

from django.conf import settings
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from pysolr import SolrError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from adminapi.inspectors.report_search_inspector import ReportSearchInspector
from eqar_backend.searchers import Searcher
from reports.models import Report


class ReportFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search')
    agency = filters.CharFilter(label='Agency')
    country = filters.CharFilter(label='Country')
    activity = filters.CharFilter(label='Activity')
    activity_type = filters.CharFilter(label='Activity Type')
    flag = filters.CharFilter(label='flag')
    active = filters.BooleanFilter(label='active')
    year = filters.NumberFilter(label='year')
    programme_type = filters.CharFilter(label='Programme Type')

    ordering = OrderingFilter(
        fields=(
            ('score', 'score'),
            ('name', 'name_sort')
        )
    )


@method_decorator(name='get', decorator=swagger_auto_schema(
   filter_inspectors=[ReportSearchInspector]
))
class ReportList(ListAPIView):
    """
    Returns a list of all the institutions to which report was submitted in DEQAR.
    """
    queryset = Report.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ReportFilterClass
    core = getattr(settings, "SOLR_CORE_REPORTS", "deqar-reports")

    def list(self, request, request_type, *args, **kwargs):
        limit = request.query_params.get('limit', 10)
        offset = request.query_params.get('offset', 0)

        filters = []
        filters_or = []

        if request_type == 'my':
            user = request.user
            filters_or.append({'user_created': user.username})

            userprofile = request.user.deqarprofile
            submitting_agency = userprofile.submitting_agency

            if submitting_agency.agency:
                filters_or.append({'agency_facet': submitting_agency.agency.acronym_primary})

        date_filters = []
        qf = [
            'institution_programme_primary^5.0',
            'institution_name_english^2.5',
            'institution_name_official^2.5',
            'institution_name_official_transliterated^2.5',
            'institution_name_version^1.5',
            'institution_name_version_transliterated^1.5',
            'programme_name^2.5',
            'country^1.5',
            'city^2',
        ]
        params = {
            'search': request.query_params.get('query', ''),
            'ordering': request.query_params.get('ordering', '-score'),
            'qf': qf,
            'fl': 'id,local_id,'
                  'agency_acronym,country,agency_esg_activity,agency_esg_activity_type,'
                  'institution_programme_primary,valid_from,valid_to,'
                  'flag_level,score,date_created,date_updated',
            'facet': True,
            'facet_fields': ['country_facet', 'flag_level_facet', 'agency_facet',
                             'activity_facet', 'activity_type_facet', 'programme_type_facet'],
            'facet_sort': 'index'
        }

        id = request.query_params.get('id', None)
        local_id = request.query_params.get('local_id', None)
        agency = request.query_params.get('agency', None)
        country = request.query_params.get('country', None)
        activity = request.query_params.get('activity', None)
        activity_type = request.query_params.get('activity_type', None)
        flag = request.query_params.get('flag', None)
        active = request.query_params.get('active', False)
        year = request.query_params.get('year', False)
        year_created = request.query_params.get('year_created', False)
        programme_type = request.query_params.get('programme_type', None)

        if id:
            filters.append({'id_search': id})
        if local_id:
            filters.append({'local_id': local_id})
        if agency:
            filters.append({'agency_facet': agency})
        if country:
            filters.append({'country_facet': country})
        if activity:
            filters.append({'activity_facet': activity})
        if activity_type:
            filters.append({'activity_type_facet': activity_type})
        if flag:
            filters.append({'flag_level_facet': flag})
        if programme_type:
            filters.append({'programme_type_facet': programme_type})
        if active:
            if active == 'true':
                now = datetime.datetime.now().replace(microsecond=0).isoformat()
                date_filters.append({'valid_to_calculated': '[%sZ TO *]' % now})
        if year:
            try:
                if re.match(r'.*([1-3][0-9]{3})', year):
                    date_from = datetime.datetime(year=int(year), month=12, day=31, hour=23, minute=59, second=59).isoformat()
                    date_filters.append({'valid_from': '[* TO %sZ]' % date_from})
                    date_to = datetime.datetime(year=int(year), month=1, day=1, hour=0, minute=0, second=0).isoformat()
                    date_filters.append({'valid_to_calculated': '[%sZ TO *]' % date_to})
            except ValueError:
                pass
        if year_created:
            try:
                if re.match(r'.*([1-3][0-9]{3})', year_created):
                    date_from = datetime.datetime(
                        year=int(year_created), month=1, day=1, hour=0, minute=0, second=1).isoformat()
                    date_to = datetime.datetime(
                        year=int(year_created), month=12, day=31, hour=23, minute=59, second=59).isoformat()
                    date_filters.append({'date_created': '[%sZ TO %sZ]' % (date_from, date_to)})
            except ValueError:
                pass

        params['filters'] = filters
        params['filters_or'] = filters_or
        params['date_filters'] = date_filters

        searcher = Searcher(self.core)
        searcher.initialize(params, start=offset, rows_per_page=limit, tie_breaker='institution_programme_sort asc')

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
