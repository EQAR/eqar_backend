from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView
from drf_rw_serializers.generics import RetrieveUpdateAPIView

from adminapi.serializers.institution_serializers import InstitutionReadSerializer, InstitutionWriteSerializer
from institutions.models import Institution


class InstitutionDetail(RetrieveUpdateAPIView):
    queryset = Institution.objects.all()
    read_serializer_class = InstitutionReadSerializer
    write_serializer_class = InstitutionWriteSerializer

    @swagger_auto_schema(responses={'200': InstitutionReadSerializer})
    def get(self, request, *args, **kwargs):
        return super(InstitutionDetail, self).get(request, *args, **kwargs)

    @swagger_auto_schema(request_body=InstitutionWriteSerializer)
    def put(self, request, *args, **kwargs):
        return super(InstitutionDetail, self).get(request, *args, **kwargs)


class InstitutionCreate(CreateAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionWriteSerializer
