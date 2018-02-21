from django.core.exceptions import ObjectDoesNotExist

from institutions.models import InstitutionCountry
from programmes.models import Programme, ProgrammeName, ProgrammeIdentifier


class ProgrammePopulator():
    """
    Class to handle the population of programme records from the submission endpoints.
    """
    def __init__(self, submission, agency, report):
        self.submission = submission
        self.agency = agency
        self.report = report
        self.programme = None

    def populate(self):
        self._create_programme()
        self._programme_name_insert()
        self._programme_identifier_insert()

    def _create_programme(self):
        countries = self.submission.get('countries', [])
        self.programme = Programme.objects.create(
            report=self.report,
            nqf_level=self.submission.get('nqf_level', ""),
            qf_ehea_level=self.submission.get('qf_ehea_level', None)
        )
        for country in countries:
            try:
                InstitutionCountry.objects.get(
                    institution__reports=self.report,
                    country=country
                )
            except ObjectDoesNotExist:
                self.programme.countries.add(country)

    def _programme_name_insert(self):
        """
        Create ProgrammeName instance.
        """
        alternative_names = self.submission.get('alternative_names', [])
        self.programme.programmename_set.create(
            name=self.submission.get('name_primary', ""),
            qualification=self.submission.get('qualification_primary', ""),
            name_is_primary=True
        )
        for an in alternative_names:
            self.programme.programmename_set.create(
                name=an.get('name_alternative', ""),
                qualification=an.get('qualification_alternative', ""),
                name_is_primary=False
            )
        self.programme.set_primary_name()

    def _programme_identifier_insert(self):
        """
        Create ProgrammeIdentifier instance.
        """
        identifiers = self.submission.get('identifiers', [])
        for idf in identifiers:
            self.programme.programmeidentifier_set.create(
                identifier=idf.get('identifier', ""),
                agency=self.agency,
                resource=idf.get('resource', 'local identifier')
            )