from django.test import TestCase

from lists.models import *


class InstitutionTestCase(TestCase):
    """
    Test module for the list classes.
    """
    fixtures = [
        'association', 'eqar_decision_type',
        'identifier_resource', 'language',
        'qf_ehea_level'
    ]

    def test_identifier_resource_str(self):
        institution_resource = IdentifierResource.objects.get(id=1)
        self.assertEqual(str(institution_resource), 'WHED')

    def test_language_str(self):
        language = Language.objects.get(id=1)
        self.assertEqual(str(language), 'Afar')

    def test_qf_ehea_level_str(self):
        qf_ehea_level = QFEHEALevel.objects.get(code=0)
        self.assertEqual(str(qf_ehea_level), 'short cycle')

    def text_association_str(self):
        association = Association.objects.get(pk=1)
        self.assertEqual(str(association), 'ENQA member')

    def test_eqar_decision_type_str(self):
        eqar_decision_type = EQARDecisionType.objects.get(pk=1)
        self.assertEqual(str(eqar_decision_type), 'renewal')
