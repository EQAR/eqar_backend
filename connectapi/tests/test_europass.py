from django.test import TestCase

from lxml import etree

from countries.models import Country
from connectapi.europass.accrediation_xml_creator_v2 import AccrediationXMLCreatorV2

class EuropassTest(TestCase):
    """
    Test module for the Europass/QDR export
    """
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eter_demo', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'programme_demo_01', 'programme_demo_02', 'programme_demo_03',
        'programme_demo_04', 'programme_demo_05', 'programme_demo_06',
        'programme_demo_07', 'programme_demo_08', 'programme_demo_09',
        'programme_demo_10', 'programme_demo_11', 'programme_demo_12',
        'report_decision', 'report_status',
        'users', 'report_demo_01'
    ]

    def test_europass_xml_creator(self):
        ctry = Country.objects.get(pk=64)
        creator = AccrediationXMLCreatorV2(ctry, check=False)
        xml = creator.create()
        self.assertEqual(xml.tag, '{http://data.europa.eu/snb/model/ap/ams-constraints/}Accreditations')

