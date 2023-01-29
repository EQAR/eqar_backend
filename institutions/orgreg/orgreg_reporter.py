from datetime import datetime


class OrgRegReporter:
    def __init__(self):
        self.report_lines = []
        self.header_lines = []
        self.institution_header_lines = []

    def add_report_line(self, line):
        self.report_lines.append(line)

    def add_divider_line(self, char, which):
        if which == 'header':
            self.header_lines.append(char * 100)
        if which == 'institution_report':
            self.report_lines.append(char * 100)
        if which == 'institution_header':
            self.institution_header_lines.append(char * 100)

    def add_empty_line(self, which):
        self.add_divider_line('', which)

    def add_header(self):
        self.add_divider_line('#', 'header')
        self.header_lines.append('OrgReg Report Sync - %s' % datetime.now())
        self.add_divider_line('#', 'header')
        self.add_divider_line('', 'header')
        print(self.get_report_lines('header'))

    def add_institution_header(self, orgreg_id, deqar_id, institution_name, action='UPDATE'):
        self.add_divider_line('-', 'institution_header')
        self.institution_header_lines.append('Institution record %s / %s (%s)' % (orgreg_id, deqar_id, action))
        self.institution_header_lines.append(institution_name)
        self.add_divider_line('-', 'institution_header')

    def print_and_reset_report(self):
        if len(self.report_lines) > 0:
            self.add_divider_line('', 'institution_report')
            print(self.get_report_lines('institution_header'))
            print(self.get_report_lines('institution_report'))
        self.reset_report()

    def get_report_lines(self, which):
        if which == 'header':
            return '\n'.join(self.header_lines)
        if which == 'institution_report':
            return '\n'.join(self.report_lines)
        if which == 'institution_header':
            return '\n'.join(self.institution_header_lines)

    def reset_report(self):
        self.header_lines = []
        self.report_lines = []
        self.institution_header_lines = []
