import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from institutions.models import InstitutionCountry
from programmes.models import Programme, ProgrammeName, ProgrammeIdentifier

logger = logging.getLogger(__name__)


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
        self._programme_learning_outcome_insert()

    def _create_programme(self):
        countries = self.submission.get('countries', [])
        self.programme = Programme.objects.create(
            report=self.report,
            nqf_level=self.submission.get('nqf_level', ""),
            qf_ehea_level=self.submission.get('qf_ehea_level', None),
            degree_outcome=self.submission.get('degree_outcome', True),
            workload_ects=self.submission.get('workload_ects', None),
            assessment_certification=self.submission.get('assessment_certification', None),
            field_study=self.submission.get('field_study', None),
            learning_outcome_description=self.submission.get('learning_outcome_description', None),
            mc_as_part_of_accreditation=self.submission.get('mc_as_part_of_accreditation', False)
        )
        for country in countries:
            count = InstitutionCountry.objects.filter(
                institution__reports=self.report,
                country=country
            ).count()
            if count == 0:
                self.programme.countries.add(country)

    def _programme_name_insert(self):
        """
        Create ProgrammeName instance.
        """
        primary_name = self.submission.get('name_primary', "")
        alternative_names = self.submission.get('alternative_names', [])
        self.programme.programmename_set.create(
            name=self.submission.get('name_primary', ""),
            qualification=self.submission.get('qualification_primary', ""),
            name_is_primary=True
        )
        for an in alternative_names:
            alt_name = an.get('name_alternative', "")
            if alt_name != primary_name:
                try:
                    self.programme.programmename_set.create(
                        name=alt_name,
                        qualification=an.get('qualification_alternative', ""),
                        name_is_primary=False
                    )
                except IntegrityError:
                    logger.error('Duplicated alternative name (%s) in report: %s! SKIPPING' %
                                 (alt_name, self.report.id))
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

    def _programme_learning_outcome_insert(self):
        """
        Create ProgrammeLearningOutcome instance.
        """
        learning_outcomes = self.submission.get('learning_outcomes', [])
        for learning_outcome in learning_outcomes:
            self.programme.programmelearningoutcome_set.create(
                learning_outcome_esco=learning_outcome
            )