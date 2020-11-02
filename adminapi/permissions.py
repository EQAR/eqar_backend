from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from accounts.models import DEQARProfile
from reports.models import Report


class CanEditReport(permissions.BasePermission):
    """
    Object-level permission to only allow users to who are able to submit for an agency.
    """

    def has_permission(self, request, view):
        deqar_profile = DEQARProfile.objects.get(user=request.user)

        if request.method == 'GET':
            return True
        else:
            try:
                report = get_object_or_404(Report, pk=view.kwargs['pk'])
                return deqar_profile.submitting_agency.agency_allowed(report.agency)
            except ObjectDoesNotExist:
                return False


class CanAccessAgency(permissions.BasePermission):
    """
    Object-level permission to only allow agencies to edit the appropriate data.
    """

    def has_permission(self, request, view):
        deqar_profile = DEQARProfile.objects.get(user=request.user)
        agency_id = view.kwargs.get('pk', 0)
        for agency_proxy in deqar_profile.submitting_agency.submitting_agency.all():
            if str(agency_proxy.allowed_agency_id) == agency_id:
                return True
        return False


class CanOperateFromDEQAROnly(permissions.BasePermission):
    """
    Object-level permission to only allow requests from deqar.eu
    """

    def has_permission(self, request, view):
        pass