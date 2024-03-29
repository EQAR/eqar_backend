from django.test import TestCase

from lists.models import *


class InstitutionTestCase(TestCase):
    """
    Test module for the list classes.
    """
    fixtures = [
        'association', 'eqar_decision_type',
        'identifier_resource', 'language',
        'qf_ehea_level', 'permission_type', 'flag'
    ]

    def test_identifier_resource_str(self):
        institution_resource = IdentifierResource.objects.get(pk='WHED')
        self.assertEqual(str(institution_resource), 'WHED')

    def test_language_str(self):
        language = Language.objects.get(id=1)
        self.assertEqual(str(language), 'Afar')

    def test_qf_ehea_level_str(self):
        qf_ehea_level = QFEHEALevel.objects.get(code=0)
        self.assertEqual(str(qf_ehea_level), 'short cycle')

    def test_association_str(self):
        association = Association.objects.get(pk=1)
        self.assertEqual(str(association), 'ENQA member')

    def test_eqar_decision_type_str(self):
        eqar_decision_type = EQARDecisionType.objects.get(pk=1)
        self.assertEqual(str(eqar_decision_type), 'renewal')

    def test_eqar_permission_type_str(self):
        eqar_permission_type = PermissionType.objects.get(pk=1)
        self.assertEqual(str(eqar_permission_type), 'yes')

    def test_eqar_flag_str(self):
        eqar_flag = Flag.objects.get(pk=2)
        self.assertEqual(str(eqar_flag), 'low level')
