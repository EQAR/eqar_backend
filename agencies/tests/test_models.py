from datetime import datetime

from django.test import TestCase

from agencies.models import *


class AgencyTestCase(TestCase):
    """
    Test module for the Agency class.
    """
    fixtures = [
        'country',
        'agency_activity_type', 'agency_enqa_membership', 'agency_focus',
        'agency_demo_01', 'agency_demo_02'
    ]

    def test_get_primary_name_metohd(self):
        agency01 = Agency.objects.get(id=1)
        agency02 = Agency.objects.get(id=2)
        self.assertEqual(agency01.get_primary_name(), 'Accreditation, Certification and Quality Assurance Institute')
        self.assertEqual(agency02.get_primary_name(), 'Estonian Quality Agency for Higher and Vocational Education')

    def test_get_primary_acronym(self):
        agency01 = Agency.objects.get(id=1)
        agency02 = Agency.objects.get(id=2)
        self.assertEqual(agency01.get_primary_acronym(), 'ACQUIN')
        self.assertEqual(agency02.get_primary_acronym(), 'EKKA')
