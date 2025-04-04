import csv
import re

from submissionapi.csv_functions.csv_insensitive_dict_reader import DictReaderInsensitive


class CSVHandler:
    """
        Class to handle CSV upload, transform it to a submission request object
    """
    FIELDS = {
        'reports': [
            r'agency',
            r'contributing_agencies\[\d+\]',
            r'report_id',
            r'local_identifier',
            r'status',
            r'decision',
            r'summary',
            r'valid_from',
            r'valid_to',
            r'date_format',
            r'other_comment'
        ],
        'activities': [
            r'activities\[\d+\]\.id',
            r'activities\[\d+\]\.local_identifier',
            r'activities\[\d+\]\.agency',
            r'activities\[\d+\]\.group',
        ],
        'report_links': [
            r'link\[\d+\]',
            r'link_display_name\[\d+\]'
        ],
        'report_files': [
            r'file\[\d+\]\.original_location',
            r'file\[\d+\]\.display_name',
            r'file\[\d+\]\.file',
            r'file\[\d+\]\.file_name',
        ],
        'report_files__report_language': [
            r'file\[\d+\]\.report_language\[\d+\]',
        ],
        'institutions': [
            r'institution\[\d+\]\.deqar_id',
            r'institution\[\d+\]\.eter_id',
            r'institution\[\d+\]\.identifier',
            r'institution\[\d+\]\.resource'
        ],
        'platforms': [
            r'platform\[\d+\]\.deqar_id',
            r'platform\[\d+\]\.eter_id',
            r'platform\[\d+\]\.identifier',
            r'platform\[\d+\]\.resource'
        ],
        'programmes': [
            r'programme\[\d+\]\.name_primary',
            r'programme\[\d+\]\.qualification_primary',
            r'programme\[\d+\]\.nqf_level',
            r'programme\[\d+\]\.qf_ehea_level',
            r'programme\[\d+\]\.degree_outcome',
            r'programme\[\d+\]\.workload_ects',
            r'programme\[\d+\]\.learning_outcome_description',
            r'programme\[\d+\]\.field_study',
            r'programme\[\d+\]\.assessment_certification',
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
        ],
        'programmes__learning_outcomes': [
            r'programme\[\d+\]\.learning_outcome\[\d+\]',
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
                self._create_activities(row)
                self._create_report_links(row)
                self._create_report_files(row)
                self._create_institutions(row)
                self._create_platforms(row)
                self._create_programmes(row)
                self._create_programmes_alternative_names(row)
                self._create_programmes_identifiers(row)
                self._create_programmes_countries(row)
                self._create_learning_outcomes(row)
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
        self.reader = DictReaderInsensitive(self.csvfile)

    def _create_report(self, row):
        csv_fields = self.reader.fieldnames
        for field in self.FIELDS['reports']:
            r = re.compile(field)
            rematch = sorted(list(filter(r.match, csv_fields)), key=str.lower)

            if len(rematch) > 0:
                if 'contributing_agencies' in field:
                    self.report_record['contributing_agencies'] = []
                    for column in rematch:
                        self.report_record['contributing_agencies'].append(row[column])
                else:
                    self.report_record[rematch[0]] = row[rematch[0]]

    def _create_activities(self, row):
        self._create_first_level_placeholder(['activities'])
        self._create_first_level_values('activities', row, dotted=True)

    def _create_institutions(self, row):
        self._create_first_level_placeholder(['institutions'])
        self._create_first_level_values('institutions', row, dotted=True)

    def _create_platforms(self, row):
        self._create_first_level_placeholder(['platforms'])
        self._create_first_level_values('platforms', row, dotted=True)

    def _create_programmes(self, row):
        self._create_first_level_placeholder(['programmes',
                                              'programmes__identifiers',
                                              'programmes__alternative_names',
                                              'programmes__countries',
                                              'programmes__learning_outcomes'])
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

    def _create_learning_outcomes(self, row):
        self._create_second_level_placeholder('programmes__learning_outcomes')
        self._create_second_level_values('programmes__learning_outcomes', row)

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

            max_index = 0
            for csv_field in csv_fields:
                match = r.match(csv_field)
                if match:
                    groups = re.search(r"\d+", csv_field)
                    index = int(groups.group(0))
                    if index > max_index:
                        max_index = index

            # Create plaholder if it doesn't exists yet
            if max_index > 0:
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

                    max_index = 0
                    for csv_field in csv_fields:
                        match = r.match(csv_field)
                        if match:
                            groups = re.search(r"\d+", csv_field)
                            index = int(groups.group(0))
                            if index > max_index:
                                max_index = index

                    # Create plaholder if it doesn't exists yet
                    if max_index > 0:
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
