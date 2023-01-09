import json
import re

from django.conf import settings
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from pysolr import SolrError
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from datetime import datetime, date
from datedelta import datedelta

from eqar_backend.searchers import Searcher
from reports.inspectors.report_list_inspector import ReportListInspector
from reports.models import Report


class ReportFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search')
    agency_id = filters.CharFilter(label='Agency ID')
    activity_id = filters.CharFilter(label='Agency ESG Activity ID')
    activity_type = filters.CharFilter(label='Activity Type')
    activity_type_id = filters.CharFilter(label='Activity Type ID')
    country_id = filters.CharFilter(label='Country')
    institution_id = filters.CharFilter(label='Institution ID')
    status = filters.CharFilter(label='Status')
    status_id = filters.CharFilter(label='Status ID')
    decision = filters.CharFilter(label='Decision')
    decision_id = filters.CharFilter(label='Decision ID')
    cross_border = filters.CharFilter(label='Cross-border')
    flag = filters.CharFilter(label='Flag')
    language = filters.CharFilter(label='Language')
    language_id = filters.CharFilter(label='Language ID')
    active = filters.BooleanFilter(label='Active')
    year = filters.NumberFilter(label='Year')
    report_date_range_from = filters.DateFilter(label='Report Date (From)')
    report_date_range_to = filters.DateFilter(label='Report Date (To)')
    report_valid_on = filters.DateFilter(label='Report Validity Date (Exact)')

    ordering = OrderingFilter(
        fields=(
            ('score', 'score'),
            ('name', 'name_sort')
        )
    )


@method_decorator(name='get', decorator=swagger_auto_schema(
   filter_inspectors=[ReportListInspector]
))
class ReportSearchView(ListAPIView):
    """
    Returns a list of all the institutions to which report was submitted in DEQAR.
    """
    queryset = Report.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ReportFilterClass
    core = getattr(settings, "SOLR_CORE_REPORTS_V3", "deqar-reports")

    def zero_or_more(self, request, field, default):
        value = request.query_params.get(field, default)
        if not str(value).isdigit():
            raise ParseError(detail='%s should be zero or larger number.' % field)
        value = default if value == '' else value
        return value

    def get_report_valid(self, valid_from, valid_to):
        valid = True
        valid_from = datetime.strptime(valid_from, '%Y-%m-%dT%H:%M:%SZ').date()
        if valid_to:
            valid_to = datetime.strptime(valid_to, '%Y-%m-%dT%H:%M:%SZ').date()

        # Check if valid_from less than equal then todays date - 6 years and valid_to isn't set
        if valid_from <= date.today()-datedelta(years=6) and valid_to is None:
            valid = False

        # Check if valid_to lest than equal then todays date
        if valid_to:
            if valid_to <= date.today():
                valid = False

        return valid

    def list(self, request, *args, **kwargs):
        limit = self.zero_or_more(request, 'limit', 10)
        offset = self.zero_or_more(request, 'offset', 0)

        filters = [{'-flag_level_facet': 'high level'}]
        filters_or = []

        date_filters = []
        qf = [
            'id_search^5.0',
            'programme_name^2.5',
            'country^1.5',
            'city^2',
        ]
        params = {
            'search': request.query_params.get('query', ''),
            'ordering': request.query_params.get('ordering', '-score'),
            'qf': qf,
            'fl': 'id,agency_esg_activity_type,agency,agency_url,contributing_agencies,'
                  'country,crossborder,date_created,date_updated,decision,flag_level,institutions,'
                  'institutions_additional,local_identifier,programmes,report_valid,status,'
                  'valid_from,valid_to,valid_to_calculated',
            'facet': True,
            'facet_fields': ['agency_id', 'country_id', 'activity_id',
                             'activity_type_facet', 'status_facet',
                             'decision_facet', 'language_facet',
                             'flag_level_facet', 'crossborder_facet'],
            'facet_sort': 'index'
        }

        agency_id = request.query_params.get('agency_id', None)
        activity_id = request.query_params.get('activity_id', None)
        activity_type = request.query_params.get('activity_type', None)
        activity_type_id = request.query_params.get('activity_type_id', None)
        country_id = request.query_params.get('country_id', None)
        institution_id = request.query_params.get('institution_id', None)

        status = request.query_params.get('status', None)
        status_id = request.query_params.get('status_id', None)

        decision = request.query_params.get('decision', None)
        decision_id = request.query_params.get('decision_id', None)

        language_id = request.query_params.get('language_id', False)

        cross_border = request.query_params.get('cross_border', None)
        flag = request.query_params.get('flag', None)
        active = request.query_params.get('active', False)
        year = request.query_params.get('year', False)

        if agency_id:
            filters.append({'agency_id': agency_id})

        if activity_id:
            filters.append({'activity_id': activity_id})

        if activity_type:
            if activity_type == 'programme' or activity_type == 'joint programme':
                filters_or.append({'activity_type_facet': 'programme'})
                filters_or.append({'activity_type_facet': 'joint programme'})
            else:
                filters.append({'activity_type_facet': activity_type})

        if activity_type_id:
            if activity_type_id == '1' or activity_type_id == '3':
                filters_or.append({'activity_type_id': '1'})
                filters_or.append({'activity_type_id': '3'})
            else:
                filters.append({'activity_type_id': activity_type_id})

        if country_id:
            filters.append({'country_id': country_id})

        if institution_id:
            filters.append({'institution_id': institution_id})

        if status:
            filters.append({'status_facet': status})
        if status_id:
            filters.append({'status_id': status_id})

        if decision:
            filters.append({'decision_facet': decision})
        if decision_id:
            filters.append({'decision_id': decision_id})

        if cross_border:
            filters.append({'crossborder_facet': cross_border})

        if language_id:
            filters.append({'language_id': language_id})

        if flag:
            filters.append({'flag_level_facet': flag})
        if active:
            if active == 'true':
                now = datetime.now().replace(microsecond=0).isoformat()
                date_filters.append({'valid_to_calculated': '[%sZ TO *]' % now})
        if year:
            try:
                if re.match(r'.*([1-3][0-9]{3})', year):
                    date_from = datetime(year=int(year), month=12, day=31, hour=23, minute=59, second=59).isoformat()
                    date_filters.append({'valid_from': '[* TO %sZ]' % date_from})
                    date_to = datetime(year=int(year), month=1, day=1, hour=0, minute=0, second=0).isoformat()
                    date_filters.append({'valid_to_calculated': '[%sZ TO *]' % date_to})
            except ValueError:
                pass

        # Handle report_date_range filters
        report_dates = ['*', '*']
        report_date_range_from = request.query_params.get('report_date_range_from', None)
        report_date_range_to = request.query_params.get('report_date_range_to', None)

        if report_date_range_from:
            try:
                d = datetime.strptime(report_date_range_from, "%Y-%m-%d")
                report_dates[0] = "%sZ" % datetime(year=d.year, month=d.month, day=d.day, hour=0, minute=0, second=0).isoformat()
            except ValueError:
                pass

        if report_date_range_to:
            try:
                d = datetime.strptime(report_date_range_to, "%Y-%m-%d")
                report_dates[1] = "%sZ" % datetime(year=d.year, month=d.month, day=d.day, hour=0, minute=0, second=0).isoformat()
            except ValueError:
                pass

        if report_dates[0] != '*' or report_dates[1] != '*':
            date_filters.append({'valid_from': '[%s TO %s]' % (report_dates[0], report_dates[1])})

        # Handle report validity filters
        report_valid_on = request.query_params.get('report_valid_on', None)

        if report_valid_on:
            try:
                d = datetime.strptime(report_valid_on, "%Y-%m-%d")
                report_valid_query_date = "%sZ" % datetime(year=d.year, month=d.month, day=d.day, hour=0, minute=0, second=0).isoformat()
                date_filters.append({'valid_from': '[* TO %s]' % report_valid_query_date})
                date_filters.append({'valid_to_calculated': '[%s TO *]' % report_valid_query_date})
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

        for r in response:
            r.update((k, json.loads(v)) for k, v in r.items() if k == 'contributing_agencies')
            r.update((k, json.loads(v)) for k, v in r.items() if k == 'institutions')
            r.update((k, json.loads(v)) for k, v in r.items() if k == 'programmes')
            r.update((k, json.loads(v)) for k, v in r.items() if k == 'country')

            if 'valid_to' in r.keys():
                r['report_valid'] = self.get_report_valid(r['valid_from'], r['valid_to'])
            else:
                r['report_valid'] = self.get_report_valid(r['valid_from'], None)

        resp = {
            'count': response.hits,
            'results': response.docs,
            'facets': response.facets
        }

        if (int(limit) + int(offset)) < int(response.hits):
            resp['next'] = True

        return Response(resp)
