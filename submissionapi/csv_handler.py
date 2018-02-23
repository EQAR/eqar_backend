import csv
import re


class CSVHandler:
    """
        Class to handle CSV upload, transform it to a submission request object
    """
    VALID_FIELD = [
        r'agency',
        r'local_identifier',
        r'activity',
        r'activity_local_identifier',
        r'status',
        r'decision',
        r'valid_from',
        r'valid_to',
        r'date_format',
        r'link\[\d+\]',
        r'link_display_name\[\d+\]',
        r'file\[\d+\]\.file_original_location',
        r'file\[\d+\]\.display_name',
        r'file\[\d+\]\.report_language\[\d+\]',
        r'institution\[\d+\]\.deqar_id',
        r'institution\[\d+\]\.eter_id',
        r'institution\[\d+\]\.identifier\[\d+\]',
        r'institution\[\d+\]\.resource\[\d+\]',
        r'institution\[\d+\]\.name_official',
        r'institution\[\d+\]\.name_official_transliterated',
        r'institution\[\d+\]\.name_english',
        r'institution\[\d+\]\.name_alternative\[\d+\]',
        r'institution\[\d+\]\.name_alternative_transliterated\[\d+\]',
        r'institution\[\d+\]\.acronym',
        r'institution\[\d+\]\.country\[\d+\]',
        r'institution\[\d+\]\.city\[\d+\]',
        r'institution\[\d+\]\.latitude\[\d+\]',
        r'institution\[\d+\]\.longitude\[\d+\]',
        r'institution\[\d+\]\.qf_ehea_level\[\d+\]',
        r'institution\[\d+\]\.website_link',
        r'programme\[\d+\]\.identifier\[\d+\]',
        r'programme\[\d+\]\.resource\[\d+\]',
        r'programme\[\d+\]\.name_primary',
        r'programme\[\d+\]\.qualification_primary',
        r'programme\[\d+\]\.name_alternative\[\d+\]',
        r'programme\[\d+\]\.qualification_alternative\[\d+\]',
        r'programme\[\d+\]\.country\[\d+\]',
        r'programme\[\d+\]\.nqf_level',
        r'programme\[\d+\]\.qf_ehea_level'
    ]

    WRAPPERS = {
        'institution': 'institutions',
        'file': 'report_files',
        'programme': 'programmes',
        'link': 'report_links',
        'link_display_name': 'report_links',
        'identifier': 'identifiers',
        'resource': 'identifiers',
        'name_alternative': 'alternative_names',
        'name_alternative_transliterated': 'alternative_names',
        'country': 'locations',
        'city': 'locations',
        'latitude': 'locations',
        'longitude': 'locations',
        'qualification_alternative': 'alternative_names'
    }

    def __init__(self, csvfile, separator):
        self.csvfile = csvfile
        self.separator = separator
        self.submission_data = []
        self.error = False
        self.error_messages = []

    def handle(self):
        if self._csv_is_valid():
            self._create_submission_data()
        else:
            self.error = True
            self.error_messages.append("CSV format is not valid.")

    def _csv_is_valid(self):
        try:
            # csv.Sniffer().sniff(self.csvfile.read(1024))
            self.csvfile.seek(0)
            return True
        except csv.Error:
            return False

    def _create_submission_data(self):
        reader = csv.DictReader(self.csvfile)
        csv_fields = reader.fieldnames

        # Iterate rows
        for row in reader:
            self.report = {}

            for field in self.VALID_FIELD:
                r = re.compile(field)
                rematch = sorted(list(filter(r.match, csv_fields)), key=str.lower)

                if len(rematch) > 0:
                    # Columns with plain column name
                    if '[' not in rematch[0]:
                        self.report[rematch[0]] = row[rematch[0]]
                    else:
                        for fld in rematch:

                            if row[fld] != "-":

                                # Columns with one []
                                if fld.count('[') == 1:

                                    # Columns with one [] and a '.'
                                    if fld.count('.') == 1:
                                        fieldz = fld.split('.')
                                        field_base = fieldz[0]
                                        field_name = fieldz[1]
                                        self._add_field(fld, field_base, field_name, row[fld])

                                    # Columns with one [] and without a '.'
                                    else:
                                        self._add_field(fld, fld, fld, row[fld])

                                # Columns with many []
                                else:
                                    fieldz = fld.split('.')
                                    field01 = fieldz[0]
                                    field02 = fieldz[1]

                                # I have to check if field01 already exists:
                                    index01 = re.search(r"\[\d+\]", field01).group()
                                    field_base01 = field01.replace(index01, "")
                                    index01 = int(re.search(r"\d+", index01).group())

                                # Check if field01 has a wrapper
                                    wrapper = self.WRAPPERS.get(field_base01, None)

                                # Check if wrapper already exists
                                    existing_wrapper = self.report.get(wrapper, None)

                                # If wrapper doesn't exists we should create it
                                    if not existing_wrapper:
                                        self.report[wrapper] = []

                                # Time to make the subfield
                                    index02 = re.search(r"\[\d+\]", field02).group()
                                    field_base02 = field02.replace(index02, "")
                                    index02 = int(re.search(r"\d+", index02).group())
                                # Subfield name is in field_base02, index number is in index02

                                # Check if there is any wrapper
                                    wrapper02 = self.WRAPPERS.get(field_base02, None)
                                # If there is no wrapper we should add the values to a list
                                    if wrapper02 is None:
                                        first_level_array = self.report[wrapper][index01-1]
                                        # We should check if key exists
                                        if field_base02 not in first_level_array.keys():
                                            first_level_array[field_base02] = [row[fld]]
                                        else:
                                            first_level_array[field_base02].append(row[fld])

                                # If there is a wrapper then we should add the values to the wrapper
                                    else:
                                        # We should check if wrapper exists
                                        if len(self.report[wrapper]) > 0:
                                            first_level_array = self.report[wrapper][index01-1]
                                            existing_wrapper02 = first_level_array.get(wrapper02, None)

                                            # If there is a wrapper already we should add the value
                                            if existing_wrapper02:
                                                if len(existing_wrapper02) >= index02:
                                                    second_level_array = first_level_array[wrapper02][index02-1]
                                                    existing_field = second_level_array.get(field_base02, None)

                                                    if existing_field is None:
                                                        second_level_array[field_base02] = row[fld]

                                            # If there is not a wrapper present we should create it
                                            else:
                                                first_level_array[wrapper02] = []
                                                d2 = {}
                                                d2[field_base02] = row[fld]
                                                first_level_array[wrapper02].append(d2)
                                        else:
                                            d = {}
                                            d[wrapper02] = []
                                            d2 = {}
                                            d2[field_base02] = row[fld]
                                            d[wrapper02].append(d2)
                                            self.report[wrapper].append(d)

            self.submission_data.append(self.report)

    def _add_field(self, field, field_base, field_name, value):
        index = re.search(r"\[\d+\]", field).group()
        field_base = field_base.replace(index, "")
        index = int(re.search(r"\d+", index).group())
        wrapper = self.WRAPPERS.get(field_base, None)
        existing_wrapper = self.report.get(wrapper, None)
        if existing_wrapper:
            if len(existing_wrapper) >= index:
                existing_wrapper[index-1][field_name] = value
        else:
            d = {}
            self.report[wrapper] = []
            d[field_name] = value
            self.report[wrapper].append(d)
