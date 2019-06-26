import pysolr
from django.conf import settings
from django.http import Http404
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from agencies.models import Agency
from countries.models import Country
from institutions.models import Institution
from webapi.inspectors.institution_search_inspector import InstitutionSearchInspector
from webapi.serializers.institution_serializers import InstitutionDetailSerializer


class InstitutionFilterClass(filters.FilterSet):
    search = filters.CharFilter(label='Search')
    country = filters.ModelChoiceFilter(label='Country', queryset=Country.objects.all(), to_field_name='name_english')
    agency = filters.ModelChoiceFilter(label='Agency', queryset=Agency.objects.all(), to_field_name='acronym_primary')

    ordering = OrderingFilter(
        fields=(
            ('score', 'score'),
            ('name', 'name_sort')
        )
    )


@method_decorator(name='get', decorator=swagger_auto_schema(
   filter_inspectors=[InstitutionSearchInspector],
))
class InstitutionList(ListAPIView):
    """
    Returns a list of all the institutions to which report was submitted in DEQAR.
    """
    queryset = Institution.objects.all()
    filter_backends = (filters.DjangoFilterBackend, )
    filter_class = InstitutionFilterClass

    def list(self, request, *args, **kwargs):
        hits = 0

        # Search params
        search = request.query_params.get('search', '*:*')
        country = request.query_params.get('country', None)
        agency = request.query_params.get('agency', None)

        cursor_mark = '*'
        fq = ['+has_report:true']
        institutions = []

        # Assemble filter queries
        if search == "":
            search = "*:*"
        if country:
            fq.append('country:%s' % country)
        if agency:
            fq.append('reports_agencies:%s' % agency)

        # Ordering params
        ordering_direction = 'asc'
        ordering = request.query_params.get('ordering', '-score')
        if ordering == '':
            ordering = '-score'

        if ordering[0] == '-':
            ordering = ordering[1:]
            ordering_direction = 'desc'
        # Tie breaker
        if ordering == 'score':
            tie_brekaer = 'name_sort asc,id asc'
        else:
            tie_brekaer = 'score desc,id asc'
        sort = "%s %s,%s" % (ordering, ordering_direction, tie_brekaer)

        solr_url = getattr(settings, "SOLR_URL", "http://localhost:8983/solr")
        core = getattr(settings, "SOLR_CORE_INSTITUTIONS_REPORTS", "deqar-institutions-reports")

        solr = pysolr.Solr("%s/%s" % (solr_url, core))
        fetch_done = False
        search_kwargs = {
            'defType': 'edismax',
            'qf': ' '.join(
                [
                    'name_official^2.5',
                    'name_official_transliterated',
                    'name_english^2.5',
                    'name_version^1.5',
                    'name_version_transliterated^1.5',
                    'country^1.5',
                    'city^2',
                    'aggregated_name_english',
                    'aggregated_name_official',
                    'aggregated_name_transliterated',
                    'aggregated_country',
                    'aggregated_city'
                ]
            ),
            'fq': ' +'.join(fq),
            'fl': 'id,eter_id,name_primary,name_sort,place,website_link,score'
        }
        while not fetch_done:
            results = solr.search(
                q=search,
                cursorMark=cursor_mark,
                sort=sort,
                **search_kwargs
            )
            if cursor_mark == results.nextCursorMark:
                fetch_done = True
            institutions += results.docs

            # Ingest URL
            for i in institutions:
                i['url'] = reverse('webapi-v1:institution-detail', args=[i['id']], request=request)

            cursor_mark = results.nextCursorMark
            hits = results.hits
        return Response({'count': hits, 'results': institutions})


class InstitutionDetailByETER(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected institution (via ETER).
    """
    serializer_class = InstitutionDetailSerializer

    def get_object(self):
        try:
            return Institution.objects.get(eter__eter_id=self.kwargs['eter_id'])
        except Institution.DoesNotExist:
            raise Http404
