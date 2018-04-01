import os
from django.test import TestCase

from submissionapi.csv_functions.csv_handler import CSVHandler


class SerializerFieldValidationTestCase(TestCase):
    def setUp(self):
        self.current_dir = os.path.dirname(os.path.realpath(__file__))

    def test_csv_is_valid(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_valid.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            self.assertTrue(csv_handler._csv_is_valid())

    def test_csv_is_invalid(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_invalid.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            self.assertFalse(csv_handler._csv_is_valid())

    def test_csv_read(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_valid.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            self.assertTrue('local_identifier' in csv_handler.reader.fieldnames)
            self.assertFalse('Local_identifier' in csv_handler.reader.fieldnames)

    def test_create_report(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_valid.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            for row in csv_handler.reader:
                csv_handler._create_report(row)
                self.assertEqual(csv_handler.report_record['agency'], 'MusiQuE')
                self.assertEqual(csv_handler.report_record['local_identifier'], 'CRDB-October14')
                break

    def test_create_first_level_placeholder(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_valid.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            csv_handler._create_first_level_placeholder(['institutions',
                                                         'institutions__identifiers',
                                                         'institutions__alternative_names',
                                                         'institutions__locations',
                                                         'institutions__qf_ehea_levels'])
            self.assertTrue('institutions' in csv_handler.report_record)
            self.assertEqual(csv_handler.report_record['institutions'][0], {})

    def test_create_first_level_values(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_programme.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            for row in csv_handler.reader:
                csv_handler._create_first_level_placeholder(["programmes"])
                csv_handler._create_first_level_values('programmes', row, dotted=True)
                self.assertEqual(csv_handler.report_record['programmes'][0]['name_primary'], 'Master of Music program')
                self.assertEqual(csv_handler.report_record['programmes'][0]['qualification_primary'], 'Master')
                break

    def test_create_second_level_placeholder(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_programme.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            csv_handler._create_first_level_placeholder(['institutions'])
            csv_handler._create_second_level_placeholder('institutions__identifiers', dictkey=True)
            self.assertTrue('identifiers' in csv_handler.report_record['institutions'][0])

    def test_create_second_level_values(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_programme.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            for row in csv_handler.reader:
                csv_handler._create_first_level_placeholder(['institutions'])
                csv_handler._create_second_level_placeholder('institutions__identifiers', dictkey=True)
                csv_handler._create_second_level_values('institutions__identifiers', row, dictkey=True)
                self.assertEqual(csv_handler.report_record['institutions'][0]['identifiers'][0]['identifier'], '67')
                break

    def test_clear_submission_data(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_programme.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            for row in csv_handler.reader:
                csv_handler._create_first_level_placeholder(["programmes"])
                csv_handler._create_first_level_placeholder(["programmes"])
                csv_handler._create_first_level_placeholder(["institutions"])
                csv_handler._create_first_level_placeholder(["institutions"])
                csv_handler._create_second_level_placeholder('institutions__identifiers', dictkey=True)
                csv_handler._create_second_level_values('institutions__identifiers', row, dictkey=True)
                csv_handler._clear_submission_data()
                self.assertFalse('reports' in csv_handler.submission_data[0])
                break