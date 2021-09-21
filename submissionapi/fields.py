import six
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from agencies.models import Agency
from countries.models import Country
from lists.models import Language, QFEHEALevel
from reports.models import ReportStatus, ReportDecision, Report


class ReportIdentifierField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        try:
            report = Report.objects.get(id=data)

            user = self.context['request'].user
            submitting_agency = user.deqarprofile.submitting_agency

            if not submitting_agency.agency_allowed(report.agency):
                raise serializers.ValidationError("You are not allowed to submit data to this Report.")

        except ObjectDoesNotExist:
            raise serializers.ValidationError("Please provide valid Report ID.")
        return report


class AgencyField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if data.isdigit():
            try:
                agency = Agency.objects.get(deqar_id=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Agency DEQAR ID.")
        else:
            try:
                agency = Agency.objects.get(acronym_primary__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Agency Acronym.")

        user = self.context['request'].user
        submitting_agency = user.deqarprofile.submitting_agency
        if not submitting_agency.agency_allowed(agency):
            raise serializers.ValidationError("You can't submit data to this Agency.")
        return agency


class ContributingAgencyField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if data.isdigit():
            try:
                agency = Agency.objects.get(deqar_id=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Agency DEQAR ID.")
        else:
            try:
                agency = Agency.objects.get(acronym_primary__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Agency Acronym.")

        return agency


class ReportStatusField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if data.isdigit():
            try:
                status = ReportStatus.objects.get(pk=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Status ID.")
        else:
            try:
                status = ReportStatus.objects.get(status__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Status.")
        return status


class ReportDecisionField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if data.isdigit():
            try:
                decision = ReportDecision.objects.get(pk=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Decision ID.")
        else:
            try:
                decision = ReportDecision.objects.get(decision__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Decision.")
        return decision


class ReportLanguageField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if len(data) == 2:
            try:
                language = Language.objects.get(iso_639_1__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid language code.")
        elif len(data) == 3:
            try:
                language = Language.objects.get(iso_639_2__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid language code.")
        else:
            raise serializers.ValidationError("Please provide valid language code.")
        return language


class QFEHEALevelField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if data.isdigit():
            try:
                qf_ehea_level = QFEHEALevel.objects.get(code=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid QF EHEA ID.")
        else:
            try:
                qf_ehea_level = QFEHEALevel.objects.get(level__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid QF EHEA level.")
        return qf_ehea_level


class CountryField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        country = data.upper()
        if len(country) == 2:
            try:
                c = Country.objects.get(iso_3166_alpha2__iexact=country)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid country code.")
        elif len(country) == 3:
            try:
                c= Country.objects.get(iso_3166_alpha3__iexact=country)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid country code.")
        else:
            raise serializers.ValidationError("Please provide valid country code.")
        return c
