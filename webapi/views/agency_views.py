import datetime
from django.db.models import Q
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter

from agencies.models import Agency
from webapi.serializers.agency_serializers import AgencyListSerializer, AgencyDetailSerializer


class AgencyList(generics.ListAPIView):
    """
        Returns a list of all the agencies in DEQAR.
    """
    queryset = Agency.objects.all()
    serializer_class = AgencyListSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('name_primary', 'acronym_primary')
    ordering = ('acronym_primary', 'name_primary')


class AgencyListByFocusCountry(AgencyList):
    """
        Returns a list of all the agencies in DEQAR operating in the submitted country.
    """
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
        return Agency.objects.filter(Q(country=self.kwargs['country']))


class AgencyDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected agency.
    """
    queryset = Agency.objects.all()
    serializer_class = AgencyDetailSerializer
