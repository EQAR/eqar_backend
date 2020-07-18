from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework import filters
from drf_rw_serializers.generics import RetrieveUpdateAPIView


from adminapi.serializers.country_serializer import CountryListSerializer, CountryReadSerializer, CountryWriteSerializer
from countries.models import Country, CountryUpdateLog


class CountryList(generics.ListCreateAPIView):
    serializer_class = CountryListSerializer
    filter_backends = (OrderingFilter, filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = ['ehea_is_member', 'external_QAA_is_permitted', 'european_approach_is_permitted',
                        'ehea_key_commitment']
    ordering = ['name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'ehea_is_member']
    search_fields = ['name_english', 'iso_3166_alpha2', 'iso_3166_alpha3']
    queryset = Country.objects.all()


class CountryDetail(RetrieveUpdateAPIView):
    queryset = Country.objects.all()
    read_serializer_class = CountryReadSerializer
    write_serializer_class = CountryWriteSerializer

    @swagger_auto_schema(request_body=CountryReadSerializer, responses={'200': CountryReadSerializer})
    def put(self, request, *args, **kwargs):
        country = Country.objects.get(id=kwargs.get('pk'))

        submit_comment = request.data.get('submit_comment', None)
        if submit_comment:
            CountryUpdateLog.objects.create(
                country=country,
                note=submit_comment,
                updated_by=request.user
            )
        else:
            CountryUpdateLog.objects.create(
                country=country,
                note='Country updated',
                updated_by=request.user
            )
        country.save()
        return super(CountryDetail, self).put(request, *args, **kwargs)
