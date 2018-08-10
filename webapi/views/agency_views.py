import datetime
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from agencies.models import Agency
from institutions.models import Institution
from reports.models import Report
from webapi.serializers.agency_serializers import AgencyListSerializer, AgencyDetailSerializer, \
    AgencyListByFocusCountrySerializer, AgencyStatsSerializer


class AgencyList(generics.ListAPIView):
    """
        Returns a list of all the agencies in DEQAR.
    """
    queryset = Agency.objects.filter(
        Q(registration_valid_to__gte=datetime.datetime.now()) |
        Q(registration_valid_to__isnull=True)
    )
    serializer_class = AgencyListSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('name_primary', 'acronym_primary')
    ordering = ('acronym_primary', 'name_primary')


class AgencyListByFocusCountry(AgencyList):
    """
        Returns a list of all the agencies in DEQAR operating in the submitted country.
    """
    serializer_class = AgencyListByFocusCountrySerializer

    def get_serializer_context(self):
        context = super(AgencyListByFocusCountry, self).get_serializer_context()
        if 'country' in self.kwargs:
            context['country_id'] = self.kwargs['country']
        return context

    def get_queryset(self):
        include_history = self.request.query_params.get('history', None)

        if include_history == 'true':
            return Agency.objects.filter(Q(agencyfocuscountry__country=self.kwargs['country']))
        else:
            return Agency.objects.filter(
                Q(agencyfocuscountry__country=self.kwargs['country']) & (
                    Q(agencyfocuscountry__country_valid_to__isnull=True) |
                    Q(agencyfocuscountry__country_valid_to__gte=datetime.datetime.now())
                )
            )


class AgencyListByOriginCountry(AgencyList):
    """
        Returns a list of all the agencies in DEQAR based in the submitted country.
    """
    def get_queryset(self):
        include_history = self.request.query_params.get('history', None)

        if include_history == 'true':
            return Agency.objects.filter(Q(country=self.kwargs['country']))
        else:
            return Agency.objects.filter(
                Q(country=self.kwargs['country']) & (
                    Q(registration_valid_to__gte=datetime.datetime.now()) |
                    Q(registration_valid_to__isnull=True)
                )
            )


class AgencyDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected agency.
    """
    queryset = Agency.objects.all()
    serializer_class = AgencyDetailSerializer


class AgencyStatsView(APIView):
    """
        Returns the number of institutions and reports per agency and per agency ESG activity.
    """
    @swagger_auto_schema(responses={200: AgencyStatsSerializer()})
    def get(self, request, agency):
        agency_counter = {}
        agency_activity_counters = []

        agency_record = get_object_or_404(Agency, pk=agency)
        agency_activities = agency_record.agencyesgactivity_set

        reports_count = Report.objects.filter(agency=agency_record).count()
        institution_count = Institution.objects.filter(
            Q(has_report=True) & Q(reports__agency=agency_record)
        ).distinct().count()

        agency_counter['reports'] = reports_count
        agency_counter['institutions'] = institution_count

        for activity in agency_activities.all():
            activity_counters = {}
            reports_count = Report.objects.filter(agency_esg_activity=activity).count()
            institution_count = Institution.objects.filter(
                Q(has_report=True) & Q(reports__agency_esg_activity=activity)
            ).distinct().count()

            if reports_count:
                activity_counters['activity_id'] = activity.id
                activity_counters['reports'] = reports_count
                activity_counters['institutions'] = institution_count
                agency_activity_counters.append(activity_counters)

        return Response(AgencyStatsSerializer({
            'agency_counter': agency_counter,
            'activity_counters': agency_activity_counters
        }).data)
