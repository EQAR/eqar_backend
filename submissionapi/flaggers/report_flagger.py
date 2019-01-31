import datetime

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist

from agencies.models import AgencyFocusCountry


class ReportFlagger:
    """
    Class to check and create flags in report records.
    """
    def __init__(self, report):
        self.report = report
        self.flag_log = []

    def check_and_set_flags(self):
        self.report.reset_flag()
        self.check_countries()
        self.check_programme_qf_ehea_level()
        # self.check_ehea_is_member()
        self.check_report_file()
        self.report.flag_log = "; ".join(self.flag_log)
        self.report.save()

    def check_countries(self):
        # InstitutionCountries
        for institution in self.report.institutions.all():
            for ic in institution.institutioncountry_set.all():
                try:
                    afc = AgencyFocusCountry.objects.get(agency=self.report.agency, country=ic.country)
                except ObjectDoesNotExist:
                    afc = AgencyFocusCountry.objects.create(
                        agency=self.report.agency,
                        country=ic.country,
                        country_is_official=False,
                        country_is_crossborder=True,
                        country_valid_from=self.report.valid_from
                    )
                    self.report.set_flag_low()
                    flag_msg = "Institution country [%s] was not on a list as an Agency Focus country for [%s]."
                    self.flag_log.append(flag_msg % (ic.country.name_english, self.report.agency.acronym_primary))
                self._check_report_status_country_is_official(afc)

        # ProgrammeCountries
        for programme in self.report.programme_set.all():
            for pc in programme.countries.all():
                try:
                    afc = AgencyFocusCountry.objects.get(agency=self.report.agency, country=pc)
                except ObjectDoesNotExist:
                    afc = AgencyFocusCountry.objects.create(
                        agency=self.report.agency,
                        country=pc,
                        country_is_official=False,
                        country_is_crossborder=True,
                        country_valid_from=self.report.valid_from
                    )
                    self.report.set_flag_low()
                    flag_msg = "Programme country [%s] was not on a list as an Agency Focus country for [%s]."
                    self.flag_log.append(flag_msg % (pc.name_english, self.report.agency.acronym_primary))
                self._check_report_status_country_is_official(afc)
                self._check_programme_country_id(pc)

    def _check_report_status_country_is_official(self, agency_focus_country):
        if self.report.status_id == 1:
            if not agency_focus_country.country_is_official:
                self.report.set_flag_high()
                flag_msg = "Report was listed as obligatory, but the Agency (%s) does not have official status " \
                           "in the institution's country (%s)"
                self.flag_log.append(flag_msg % (self.report.agency.acronym_primary,
                                                 agency_focus_country.country.name_english))

    def _check_programme_country_id(self, country):
        ic_count = self.report.institutions.filter(institutioncountry__country=country).count()
        if ic_count == 0:
            self.report.set_flag_low()
            flag_msg = "Programme country [%s] is not amongst the countries of the institution(s)."
            self.flag_log.append(flag_msg % country)

    def check_programme_qf_ehea_level(self):
        for programme in self.report.programme_set.all():
            qf_ehea_level = programme.qf_ehea_level
            if qf_ehea_level is not None:
                for institution in self.report.institutions.all():
                    if institution.institutionqfehealevel_set.count() != 0:
                        if institution.institutionqfehealevel_set.filter(
                            qf_ehea_level=qf_ehea_level,
                            qf_ehea_level_verified=True
                        ).count() == 0:
                            self.report.set_flag_high()
                            flag_msg = "QF-EHEA Level [%s] for programme [%s] should be in the institutions " \
                                       "QF-EHEA level list."
                            self.flag_log.append(flag_msg % (qf_ehea_level, programme.name_primary))

    def check_validity_date(self):
        if self.report.valid_to < datetime.datetime.now() - relativedelta(years=1):
            self.report.set_flag_low()
            flag_msg = "Report validity is more then one year old."
            self.flag_log.append(flag_msg)

    def check_ehea_is_member(self):
        for institution in self.report.institutions.all():
            for ic in institution.institutioncountry_set.all():
                if ic.country.ehea_is_member:
                    if institution.institutionqfehealevel_set.count() == 0:
                        self.report.set_flag_low()
                        flag_msg = "A record was created/identified for an institution (%s) " \
                                   "in an EHEA member country (%s) without including QF-EHEA levels."
                        self.flag_log.append(flag_msg % (ic.institution.name_primary, ic.country.name_english))

    def check_report_file(self):
        for rf in self.report.reportfile_set.all():
            if rf.file_original_location == "" and rf.file.name == "":
                self.report.set_flag_low()
                self.flag_log.append("File location was not provided.")