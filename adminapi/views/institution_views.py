from rest_framework.generics import CreateAPIView
from drf_rw_serializers.generics import RetrieveUpdateAPIView

from adminapi.serializers.institution_serializers import InstitutionReadSerializer, InstitutionWriteSerializer
from institutions.models import Institution


class InstitutionDetail(RetrieveUpdateAPIView):
    queryset = Institution.objects.all()
    read_serializer_class = InstitutionReadSerializer
    write_serializer_class = InstitutionWriteSerializer


class InstitutionCreate(CreateAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionWriteSerializer
