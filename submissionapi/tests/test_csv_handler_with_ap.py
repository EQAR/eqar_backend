import os
from django.test import TestCase

from submissionapi.csv_functions.csv_handler import CSVHandler


class CSVHandlerWithAPTestCase(TestCase):
    def setUp(self):
        self.current_dir = os.path.dirname(os.path.realpath(__file__))

    def test_csv_is_valid(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_valid_ap.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            self.assertTrue(csv_handler._csv_is_valid())

    def test_csv_read(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_valid_ap.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            self.assertTrue('local_identifier' in csv_handler.reader.fieldnames)
            self.assertFalse('Local_identifier' in csv_handler.reader.fieldnames)

    def test_create_report(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_valid_ap.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            for row in csv_handler.reader:
                csv_handler._create_report(row)
                self.assertEqual(csv_handler.report_record['agency'], 'ACQUIN')
                self.assertEqual(csv_handler.report_record['local_identifier'], 'LOCAL001')
                break

    def test_create_first_level_values(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_valid_ap.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            for row in csv_handler.reader:
                csv_handler._create_first_level_placeholder(["programmes"])
                csv_handler._create_first_level_values('programmes', row, dotted=True)
                self.assertEqual(csv_handler.report_record['programmes'][0]['name_primary'], 'Programme name')
                self.assertEqual(csv_handler.report_record['programmes'][0]['workload_ects'], '15')
                break
