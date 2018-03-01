import datetime


class InstitutionFlagMessageCreator:
    """
    Class to create flag messages in institution records.
    """
    messages = {
        'name_english': '[name_english] [%s] provided by [%s]',
        'name_english_alternative': 'Alternative [name_english] [%s] suggested by [%s]',
        'acronym': 'Alternative [acronym] [%s] suggested by [%s]',
        'name_official': 'Alternative [name_official] [%s] suggested by [%s]',
        'alternative_name': '[name_version] [%s] provided by [%s]',
        'country': 'Alternative [country] [%s] suggested by [%s]',
        'city': 'Alternative [city] [%s] suggested by [%s]',
        'qf_ehea_level': 'Additional [qf_ehea_level] [%s] suggested by [%s]'
    }

    def __init__(self, agency):
        self.agency = agency
        self.collected_flag_msg = []

    def get_message(self, message_code, value):
        if message_code in self.messages:
            msg = self.messages[message_code] % (value, self.agency.acronym_primary)
            self.collected_flag_msg.append('%s on [%s]' % (msg, datetime.date.today().strftime("%Y-%m-%d")))
            return msg
        return ""
