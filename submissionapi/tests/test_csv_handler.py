import os
from django.test import TestCase

from submissionapi.csv_functions.csv_handler import CSVHandler


class CSVHandlerTestCase(TestCase):
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

    def test_create_report_with_cooauthor_agencies(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_coauthor_agency_valid.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            for row in csv_handler.reader:
                csv_handler._create_report(row)
                self.assertEqual(csv_handler.report_record['contributing_agencies'][0], 'A3ES')
                self.assertEqual(csv_handler.report_record['contributing_agencies'][1], 'ASIIN')
                break

    def test_create_first_level_placeholder(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_valid.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            csv_handler._create_first_level_placeholder(['report_files',
                                                         'report_files__report_language'])
            self.assertTrue('report_files' in csv_handler.report_record)
            self.assertEqual(csv_handler.report_record['report_files'][0], {})

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
            csv_handler._create_first_level_placeholder(['programmes'])
            csv_handler._create_second_level_placeholder('programmes__identifiers', dictkey=True)
            self.assertTrue('identifiers' in csv_handler.report_record['programmes'][0])

    def test_create_second_level_values(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_programme.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            for row in csv_handler.reader:
                csv_handler._create_first_level_placeholder(['programmes'])
                csv_handler._create_second_level_placeholder('programmes__identifiers', dictkey=True)
                csv_handler._create_second_level_values('programmes__identifiers', row, dictkey=True)
                self.assertEqual(csv_handler.report_record['programmes'][0]['identifiers'][0]['identifier'], '12')
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
                csv_handler._create_second_level_placeholder('programmes__identifiers', dictkey=True)
                csv_handler._create_second_level_values('programmes__identifiers', row, dictkey=True)
                csv_handler._clear_submission_data()
                self.assertFalse('reports' in csv_handler.submission_data[0])
                break

    def test_handle(self):
        file = os.path.join(self.current_dir, "csv_test_files", "test_programme.csv")
        with open(file, 'r') as csv_file:
            csv_handler = CSVHandler(csvfile=csv_file)
            csv_handler._read_csv()
            csv_handler.handle()
            self.assertEqual(len(csv_handler.submission_data), 2)
            self.assertEqual(csv_handler.submission_data[0]['institutions'][0]['identifier'],
                             '67')
            self.assertEqual(csv_handler.submission_data[1]['institutions'][0]['eter_id'],
                             'DE0140')
