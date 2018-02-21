from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions

from accounts.models import DEQARProfile
from reports.models import ReportFile


class CanSubmitToAgency(permissions.BasePermission):
    """
    Object-level permission to only allow users who are allowed to submit for a particular agency.
    """

    def has_permission(self, request, view):
        deqar_profile = DEQARProfile.objects.get(user=request.user)

        try:
            report_file = ReportFile.objects.get(pk=view.kwargs['pk'])
            return deqar_profile.submitting_agency.agency_allowed(report_file.report.agency)
        except ObjectDoesNotExist:
            return False
