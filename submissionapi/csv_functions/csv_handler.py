import csv

import itertools
import re

from submissionapi.csv_functions.csv_insensitive_dict_reader import DictReaderInsensitive


class CSVHandler:
    """
        Class to handle CSV upload, transform it to a submission request object
    """
    FIELDS = {
        'reports': [
            r'agency',
            r'local_identifier',
            r'activity',
            r'activity_local_identifier',
            r'status',
            r'decision',
            r'valid_from',
            r'valid_to',
            r'date_format'
        ],
        'report_links': [
            r'link\[\d+\]',
            r'link_display_name\[\d+\]'
        ],
        'report_files': [
            r'file\[\d+\]\.original_location',
            r'file\[\d+\]\.display_name',
        ],
        'report_files__report_language': [
            r'file\[\d+\]\.report_language\[\d+\]',
        ],
        'institutions': [
            r'institution\[\d+\]\.deqar_id',
            r'institution\[\d+\]\.eter_id',
            r'institution\[\d+\]\.name_official',
            r'institution\[\d+\]\.name_official_transliterated',
            r'institution\[\d+\]\.name_english',
            r'institution\[\d+\]\.acronym',
            r'institution\[\d+\]\.website_link'
        ],
        'institutions__identifiers': [
            r'institution\[\d+\]\.identifier\[\d+\]',
            r'institution\[\d+\]\.resource\[\d+\]',
        ],
        'institutions__alternative_names': [
            r'institution\[\d+\]\.name_alternative\[\d+\]',
            r'institution\[\d+\]\.name_alternative_transliterated\[\d+\]',
        ],
        'institutions__locations': [
            r'institution\[\d+\]\.country\[\d+\]',
            r'institution\[\d+\]\.city\[\d+\]',
            r'institution\[\d+\]\.latitude\[\d+\]',
            r'institution\[\d+\]\.longitude\[\d+\]',
        ],
        'institutions__qf_ehea_levels': [
            r'institution\[\d+\]\.qf_ehea_level\[\d+\]',
        ],
        'programmes': [
            r'programme\[\d+\]\.name_primary',
            r'programme\[\d+\]\.qualification_primary',
            r'programme\[\d+\]\.nqf_level',
            r'programme\[\d+\]\.qf_ehea_level'
        ],
        'programmes__identifiers': [
            r'programme\[\d+\]\.identifier\[\d+\]',
            r'programme\[\d+\]\.resource\[\d+\]',
        ],
        'programmes__alternative_names': [
            r'programme\[\d+\]\.name_alternative\[\d+\]',
            r'programme\[\d+\]\.qualification_alternative\[\d+\]',
        ],
        'programmes__countries': [
            r'programme\[\d+\]\.country\[\d+\]',
        ]
    }

    def __init__(self, csvfile):
        self.csvfile = csvfile
        self.submission_data = []
        self.report_record = {}
        self.error = False
        self.error_message = ""
        self.dialect = None
        self.reader = None

    def handle(self):
        if self._csv_is_valid():
            self._read_csv()
            for row in self.reader:
                self._create_report(row)
                self._create_report_links(row)
                self._create_report_files(row)
                self._create_institutions(row)
                self._create_institutions_identifiers(row)
                self._create_institutions_alternative_names(row)
                self._create_institutions_locations(row)
                self._create_institutions_qf_ehea_levels(row)
                self._create_programmes(row)
                self._create_programmes_alternative_names(row)
                self._create_programmes_identifiers(row)
                self._create_programmes_countries(row)
                self._clear_submission_data()
        else:
            self.error = True
            self.error_message = 'The CSV file appears to be invalid.'

    def _csv_is_valid(self):
        try:
            self.csvfile.seek(0)
            self.dialect = csv.Sniffer().sniff(self.csvfile.read(), delimiters=['\t', ',', ';'])
            return True
        except csv.Error:
            return False

    def _read_csv(self):
        self.csvfile.seek(0)
        self.reader = DictReaderInsensitive(self.csvfile, dialect=self.dialect)

    def _create_report(self, row):
        csv_fields = self.reader.fieldnames
        for field in self.FIELDS['reports']:
            r = re.compile(field)
            rematch = sorted(list(filter(r.match, csv_fields)), key=str.lower)

            if len(rematch) > 0:
                self.report_record[rematch[0]] = row[rematch[0]]

    def _create_institutions(self, row):
        self._create_first_level_placeholder(['institutions',
                                              'institutions__identifiers',
                                              'institutions__alternative_names',
                                              'institutions__locations',
                                              'institutions__qf_ehea_levels'])
        self._create_first_level_values('institutions', row, dotted=True)

    def _create_institutions_identifiers(self, row):
        self._create_second_level_placeholder('institutions__identifiers', dictkey=True)
        self._create_second_level_values('institutions__identifiers', row, dictkey=True)

    def _create_institutions_alternative_names(self, row):
        self._create_second_level_placeholder('institutions__alternative_names', dictkey=True)
        self._create_second_level_values('institutions__alternative_names', row, dictkey=True)

    def _create_institutions_locations(self, row):
        self._create_second_level_placeholder('institutions__locations', dictkey=True)
        self._create_second_level_values('institutions__locations', row, dictkey=True)

    def _create_institutions_qf_ehea_levels(self, row):
        self._create_second_level_placeholder('institutions__qf_ehea_levels')
        self._create_second_level_values('institutions__qf_ehea_levels', row)

    def _create_programmes(self, row):
        self._create_first_level_placeholder(['programmes',
                                              'programmes__identifiers',
                                              'programmes__alternative_names',
                                              'programmes__countries'])
        self._create_first_level_values('programmes', row, dotted=True)

    def _create_programmes_identifiers(self, row):
        self._create_second_level_placeholder('programmes__identifiers', dictkey=True)
        self._create_second_level_values('programmes__identifiers', row, dictkey=True)

    def _create_programmes_alternative_names(self, row):
        self._create_second_level_placeholder('programmes__alternative_names', dictkey=True)
        self._create_second_level_values('programmes__alternative_names', row, dictkey=True)

    def _create_programmes_countries(self, row):
        self._create_second_level_placeholder('programmes__countries')
        self._create_second_level_values('programmes__countries', row)

    def _create_report_links(self, row):
        self._create_first_level_placeholder(['report_links'])
        self._create_first_level_values('report_links', row)

    def _create_report_files(self, row):
        self._create_first_level_placeholder(['report_files', 'report_files__report_language'])
        self._create_first_level_values('report_files', row, dotted=True)

        self._create_second_level_placeholder('report_files__report_language')
        self._create_second_level_values('report_files__report_language', row)

    def _create_first_level_placeholder(self, field_key_array):
        fields = []
        wrapper = field_key_array[0].split('__')[0]
        csv_fields = self.reader.fieldnames

        for fk in field_key_array:
            fields += self.FIELDS[fk]

        # Create wrapper
        self.report_record[wrapper] = []

        for field in fields:
            r = re.compile(field)
            rematch = sorted(list(filter(r.match, csv_fields)), key=str.lower, reverse=True)

            # Create plaholder if it doesn't exists yet
            if len(rematch) > 0:
                rematch[0] = rematch[0].split('.')[0]
                max_index = int(re.search(r"\d+", rematch[0]).group())
                for i in range(0, max_index):
                    if len(self.report_record[wrapper]) < i+1:
                        self.report_record[wrapper].append({})

    def _create_first_level_values(self, wrapper, row, dotted=False):
        csv_fields = self.reader.fieldnames
        for field in self.FIELDS[wrapper]:
            r = re.compile(field)
            rematch = sorted(list(filter(r.match, csv_fields)), key=str.lower)

            if len(rematch) > 0:
                for fld in rematch:
                    if row[fld] != '-':
                        index = re.search(r"\[\d+\]", fld).group()
                        field = fld.replace(index, "")
                        index = int(re.search(r"\d+", index).group())-1
                        if dotted:
                            field = field.split('.')[1]
                        self.report_record[wrapper][index][field] = row[fld]

    def _create_second_level_placeholder(self, field_key, dictkey=None):
        csv_fields = self.reader.fieldnames
        first_level_wrapper_name, wrapper = field_key.split('__')

        # Create second level wrapper
        first_level_wrapper = self.report_record[first_level_wrapper_name]

        for first_level_wrapper_item in first_level_wrapper:
            first_level_wrapper_item[wrapper] = []

            if dictkey:
                for field in self.FIELDS[field_key]:
                    r = re.compile(field)
                    rematch = sorted(list(filter(r.match, csv_fields)), key=str.lower, reverse=True)

                    # Create plaholder if it doesn't exists yet
                    if len(rematch) > 0:
                        field02 = rematch[0].split('.')[1]
                        max_index = int(re.search(r"\d+", field02).group())
                        for i in range(0, max_index):
                            if len(first_level_wrapper_item[wrapper]) < i+1:
                                first_level_wrapper_item[wrapper].append({})

    def _create_second_level_values(self, field_key, row, dictkey=None):
        csv_fields = self.reader.fieldnames
        first_level_wrapper_name, wrapper = field_key.split('__')
        first_level_wrapper = self.report_record[first_level_wrapper_name]

        for field in self.FIELDS[field_key]:
            r = re.compile(field)
            rematch = sorted(list(filter(r.match, csv_fields)), key=str.lower)

            if len(rematch) > 0:
                for fld in rematch:
                    if row[fld] != '-':
                        [field01, field02] = fld.split('.')
                        index01 = int(re.search(r"\d+", field01).group())

                        index02 = re.search(r"\[\d+\]", field02).group()
                        field02 = field02.replace(index02, "")
                        index02 = int(re.search(r"\d+", index02).group())
                        if dictkey:
                            first_level_wrapper[index01-1][wrapper][index02-1][field02] = row[fld]
                        else:
                            first_level_wrapper[index01-1][wrapper].append(row[fld])

    def _clear_submission_data(self):
        self.submission_data.append(self.clean_empty(self.report_record))

    def clean_empty(self, d):
        if not isinstance(d, (dict, list)):
            return d
        if isinstance(d, list):
            return [v for v in (self.clean_empty(v) for v in d) if v]
        return {k: v for k, v in ((k, self.clean_empty(v)) for k, v in d.items()) if v}