from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView
from drf_rw_serializers.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser

from adminapi.serializers.institution_serializers import InstitutionReadSerializer, \
    InstitutionAdminWriteSerializer, InstitutionUserWriteSerializer
from institutions.models import Institution, InstitutionUpdateLog


class InstitutionDetail(RetrieveUpdateAPIView):
    queryset = Institution.objects.all()
    read_serializer_class = InstitutionReadSerializer

    def get_write_serializer_class(self, *args, **kwargs):
        if self.request.user.is_staff:
            return InstitutionAdminWriteSerializer
        else:
            return InstitutionUserWriteSerializer

    @swagger_auto_schema(responses={'200': InstitutionReadSerializer})
    def get(self, request, *args, **kwargs):
        return super(InstitutionDetail, self).get(request, *args, **kwargs)

    @swagger_auto_schema(request_body=InstitutionAdminWriteSerializer)
    def put(self, request, *args, **kwargs):
        institution = Institution.objects.get(id=kwargs.get('pk'))

        submit_comment = request.data.get('submit_comment', None)
        if submit_comment:
            InstitutionUpdateLog.objects.create(
                institution=institution,
                note=submit_comment,
                updated_by=request.user
            )
        else:
            InstitutionUpdateLog.objects.create(
                institution=institution,
                note='Institution updated',
                updated_by=request.user
            )
        institution.save()
        return super(InstitutionDetail, self).put(request, *args, **kwargs)


class InstitutionCreate(CreateAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionAdminWriteSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        institution = serializer.save(created_by=self.request.user)
        institution.save()