from datetime import datetime


class OrgRegReporter:
    def __init__(self):
        self.report_lines = []

    def add_report_line(self, line):
        self.report_lines.append(line)

    def add_divider_line(self, char):
        self.report_lines.append(char * 100)

    def add_header(self):
        self.add_divider_line('#')
        self.add_report_line('OrgReg Report Sync - %s' % datetime.now())
        self.add_divider_line('#')
        self.add_empty_line()

    def add_empty_line(self):
        self.add_report_line('')

    def add_institution_header(self, orgreg_id, deqar_id, institution_name, action='UPDATE'):
        self.add_divider_line('-')
        self.add_report_line('Institution record %s / %s (%s)' % (orgreg_id, deqar_id, action))
        self.add_report_line(institution_name)
        self.add_divider_line('-')

    def get_report(self):
        return '\n'.join(self.report_lines)

    def reset_report(self):
        self.report_lines = []
