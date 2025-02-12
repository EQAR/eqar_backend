from rest_framework.exceptions import ValidationError
from eqar_backend.serializer_fields.boolean_extended_serializer_field import BooleanExtendedField
from rest_framework.test import APITestCase


class SerializerFieldTestCase(APITestCase):
    def test_boolean_field_boolean(self):
        field = BooleanExtendedField()
        self.assertEqual(field.to_internal_value(True), True)


    def test_boolean_field_not_boolean_and_not_string(self):
        field = BooleanExtendedField()
        with self.assertRaisesRegex(ValidationError, 'Incorrect type.'):
            field.to_internal_value(1)


    def test_boolean_field_with_true_values(self):
        accepted_yes_values = ['Yes', 'yes', 'TRUE', 'True', 'true']
        field = BooleanExtendedField()
        for value in accepted_yes_values:
            value = field.to_internal_value(value)
            self.assertEqual(value, True)


    def test_boolean_field_with_false_values(self):
        accepted_no_values = ['No', 'no', 'FALSE', 'False', 'false']
        field = BooleanExtendedField()
        for value in accepted_no_values:
            value = field.to_internal_value(value)
            self.assertEqual(value, False)


    def test_boolean_field_with_not_ok_values(self):
        field = BooleanExtendedField()
        with self.assertRaisesRegex(ValidationError, 'Incorrect value.'):
            field.to_internal_value("Nope")
