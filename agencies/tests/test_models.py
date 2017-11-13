from datetime import datetime

from django.test import TestCase

from agencies.models import *


class AgencyTestCase(TestCase):
    """
    Test module for the Agency class.
    """
    def setUp(self):
        agency = Agency.objects.create(
            eqar_id='EQAR0001',
            contact_person='John Doe',
            website_link='www.eqar.eu',
            reports_link='www.eqar.eu/reports_link',
            description_note='Lorem Ipsum',
            registration_start='2007-12-15',
            registration_valid_to='2017-11-15',
            enqua_membership=AgencyENQUAMembership.objects.create(
                    membership='affiliate'
            )
        )

        AgencyFocus.objects.create(
            focus='international'
        )

        agency_name = AgencyName.objects.create(
            agency=agency,
            name_note='EQAR Name Versions Test',
            valid_to=datetime.now()
        )

        AgencyNameVersion.objects.create(
            agency_name=agency_name,
            name='EQAR Version 1',
            name_is_primary=True,
            acronym='EQAR V1',
            acronym_is_primary=True
        )

        AgencyPhone.objects.create(
            agency=agency,
            phone='12345678'
        )

    def test_agency_enqua_membership_was_created(self):
        affiliate = AgencyENQUAMembership.objects.get(membership='affiliate')
        self.assertEqual(affiliate.membership, 'affiliate')

    def test_agency_was_created(self):
        agency = Agency.objects.get(eqar_id='EQAR0001')
        self.assertEqual(agency.eqar_id, 'EQAR0001')

    def test_agency_focus_was_created(self):
        agency_focus = AgencyFocus.objects.get(focus='international')
        self.assertEqual(agency_focus.focus, 'international')

    def test_agency_name_was_created(self):
        agency = Agency.objects.get(eqar_id='EQAR0001')
        agency_name = AgencyName.objects.get(agency=agency)
        self.assertEqual(agency_name.name_note, 'EQAR Name Versions Test')

    def test_agency_name_version_was_created(self):
        agency = Agency.objects.get(eqar_id='EQAR0001')
        agency_name = AgencyName.objects.get(agency=agency)
        agency_name_version = AgencyNameVersion.objects.get(agency_name=agency_name)
        self.assertEquals(agency_name_version.acronym, 'EQAR V1')

    def test_agency_phone_was_created(self):
        agency = Agency.objects.get(eqar_id='EQAR0001')
        phone = AgencyPhone.objects.get(agency=agency)
        self.assertEqual(phone.phone, '12345678')

