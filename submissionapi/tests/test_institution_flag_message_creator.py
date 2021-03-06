import datetime
from django.test import TestCase

from agencies.models import Agency
from submissionapi.flaggers.institution_flag_message_creator import InstitutionFlagMessageCreator


class InstitutionFlagMessageCreatorTestCase(TestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'flag',
        'agency_historical_field',
        'agency_activity_type', 'agency_focus', 'permission_type',
        'eqar_decision_type',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo'
    ]

    def test_init(self):
        flagger = InstitutionFlagMessageCreator(agency=Agency.objects.get(pk=5))
        self.assertEqual(flagger.agency.acronym_primary, "ACQUIN")

    def test_get_message(self):
        flagger = InstitutionFlagMessageCreator(agency=Agency.objects.get(pk=5))
        self.assertEqual(flagger.get_message('name_english', 'EnglishName'),
                         "[name_english] [EnglishName] provided by [ACQUIN]")
