import datetime
import re

from django.conf import settings
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from adminapi.inspectors.report_search_inspector import ReportSearchInspector
from eqar_backend.searchers import Searcher
from reports.models import Report


class ReportFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search')
    agency = filters.CharFilter(label='Agency')
    country = filters.CharFilter(label='Country')
    activity_type = filters.CharFilter(label='Activity Type')
    flag = filters.CharFilter(label='flag')
    active = filters.BooleanFilter(label='active')
    year = filters.NumberFilter(label='year')

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
    filter_class = ReportFilterClass
    core = getattr(settings, "SOLR_CORE_REPORTS_ALL", "deqar-reports-all")

    def list(self, request, *args, **kwargs):
        limit = request.query_params.get('limit', 10)
        offset = request.query_params.get('offset', 0)

        filters = []
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
            'eter_id^2'
        ]
        params = {
            'search': request.query_params.get('query', ''),
            'ordering': request.query_params.get('ordering', '-score'),
            'qf': qf,
            'fl': 'id,agency,country,activity,activity_type,institution_programme_primary,valid_from,valid_to,'
                  'flag_level,score'
        }

        country = request.query_params.get('country', None)
        agency = request.query_params.get('agency', None)
        activity_type = request.query_params.get('activity_type', None)
        flag = request.query_params.get('flag', None)
        active = request.query_params.get('active', False)
        year = request.query_params.get('year', False)

        if country:
            filters.append({'country': country})
        if agency:
            filters.append({'agency': agency})
        if activity_type:
            filters.append({'activity_type': activity_type})
        if flag:
            filters.append({'flag_level': flag})
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

        params['filters'] = filters
        params['date_filters'] = date_filters

        searcher = Searcher(self.core)
        searcher.initialize(params, start=offset, rows_per_page=limit, tie_breaker='institution_programme_sort asc')
        response = searcher.search()
        resp = {
            'count': response.hits,
            'results': response.docs,
        }
        if (int(limit) + int(offset)) < int(response.hits):
            resp['next'] = True
        return Response(resp)


@method_decorator(name='get', decorator=swagger_auto_schema(
   filter_inspectors=[ReportSearchInspector]
))
class MyReportList(ListAPIView):
    """
    Returns a list of all the institutions to which report was submitted in DEQAR.
    """
    queryset = Report.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ReportFilterClass
    core = getattr(settings, "SOLR_CORE_REPORTS_ALL", "deqar-reports-all")

    def list(self, request, *args, **kwargs):
        limit = request.query_params.get('limit', 10)
        offset = request.query_params.get('offset', 0)

        filters = [{'user_created': request.user.username}]
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
            'eter_id^2'
        ]
        params = {
            'search': request.query_params.get('query', ''),
            'ordering': request.query_params.get('ordering', '-score'),
            'qf': qf,
            'fl': 'id,agency,country,activity,activity_type,institution_programme_primary,valid_from,valid_to,'
                  'flag_level,score,date_created,date_updated'
        }

        country = request.query_params.get('country', None)
        activity = request.query_params.get('activity', None)
        flag = request.query_params.get('flag', None)
        active = request.query_params.get('active', False)
        year = request.query_params.get('year', False)
        year_created = request.query_params.get('year_created', False)

        if country:
            filters.append({'country': country})
        if activity:
            filters.append({'activity': activity})
        if flag:
            filters.append({'flag_level': flag})
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
        params['date_filters'] = date_filters

        searcher = Searcher(self.core)
        searcher.initialize(params, start=offset, rows_per_page=limit, tie_breaker='institution_programme_sort asc')
        response = searcher.search()
        resp = {
            'count': response.hits,
            'results': response.docs,
        }
        if (int(limit) + int(offset)) < int(response.hits):
            resp['next'] = True
        return Response(resp)