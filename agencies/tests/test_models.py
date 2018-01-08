from datetime import datetime

from django.test import TestCase

from agencies.models import *
from lists.models import Association


class AgencyTestCase(TestCase):
    """
    Test module for the Agency class.
    """
    fixtures = [
        'country_qa_requirement_type', 'country',
        'agency_activity_type', 'agency_focus',
        'agency_demo_01', 'agency_demo_02', 'association'
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

    def test_agency_activity_type_str(self):
        agency_activity_type01 = AgencyActivityType.objects.get(id=1)
        self.assertEqual(str(agency_activity_type01), 'programme')

    def test_agency_membership_str(self):
        agency_membership = AgencyMembership.objects.create(agency=Agency.objects.get(id=1),
                                                            association=Association.objects.get(id=1))
        self.assertEqual(str(agency_membership), 'ENQA member')

    def test_agency_historical_field_str(self):
        ahf = AgencyHistoricalField.objects.create(field='country')
        self.assertEqual(str(ahf), 'country')

    def test_agency_focus_str(self):
        af = AgencyGeographicalFocus.objects.get(id=1)
        self.assertEqual(str(af), 'regional')

    def test_agency_phone_str(self):
        ap = AgencyPhone.objects.get(id=1)
        self.assertEqual(str(ap), '+49 921 530390 77')

    def test_agency_email_str(self):
        ae = AgencyEmail.objects.get(id=1)
        self.assertEqual(str(ae), 'handke@acquin.org')

    def test_agency_focus_country_str(self):
        afc = AgencyFocusCountry.objects.get(id=1)
        self.assertEqual(str(afc), 'Austria')

    def test_agency_esg_activity_str(self):
        aea = AgencyESGActivity.objects.get(id=1)
        self.assertEqual(str(aea), 'ACQUIN -> System Accreditation in Germany (programme)')
