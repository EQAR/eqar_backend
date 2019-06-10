from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions

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
                report = Report.objects.get(pk=view.kwargs['pk'])
                return deqar_profile.submitting_agency.agency_allowed(report.agency)
            except ObjectDoesNotExist:
                return False
