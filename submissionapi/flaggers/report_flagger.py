import datetime

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist

from agencies.models import AgencyFocusCountry
from institutions.models import InstitutionCountry
from lists.models import Flag
from reports.models import ReportFlag


class ReportFlagger:
    """
    Class to check and create flags in report records.
    """
    def __init__(self, report):
        self.report = report
        self.flag_msg = {
            'institutionCountry': 'Institution country [%s] was not on a list as an Agency Focus country for [%s].',
            'programmeCountry': 'Programme country [%s] was not on a list as an Agency Focus country for [%s].',
            'statusCountryIsOfficial': "Report was listed as obligatory, but the Agency (%s) does not have official "
                                       "status in the institution's country (%s)",
            'statusCountryIsOfficialMultiInstitution': "Report was listed as obligatory, but the Agency (%s) "
                                                       "does not have official "
                                                       "status in any of the institution's country",
            'programmeCountryId': 'Programme country [%s] is not amongst the countries of the institution(s).',
            'programmeQFEHEALevel': 'QF-EHEA Level [%s] for programme [%s] should be in the institutions '
                                    'QF-EHEA level list.',
            'validityDate': 'Report validity is more then one year old.',
            'EHEAIsMember': 'A record was created/identified for an institution (%s) in an EHEA member country (%s) '
                            'without including QF-EHEA levels.',
            'file': 'File location was not provided.'
        }

    def check_and_set_flags(self):
        self.reset_flag()
        self.check_countries()
        self.check_report_status_country_is_official_for_multi_institution()

        self.check_programme_qf_ehea_level()
        # self.check_ehea_is_member()
        self.check_report_file()
        self.set_flag()
        self.report.save()

    def reset_flag(self):
        self.report.flag = Flag.objects.get(pk=1)
        for report_flag in self.report.reportflag_set.iterator():
            report_flag.active = False
            report_flag.save()
        self.report.save()

    def add_flag(self, flag_level, flag_message):
        flag = Flag.objects.get(pk=flag_level)
        report_flag, created = ReportFlag.objects.get_or_create(
            report=self.report,
            flag=flag,
            flag_message=flag_message
        )
        if not report_flag.removed_by_eqar:
            report_flag.active = True
            report_flag.save()

    def set_flag(self):
        self.report.flag = Flag.objects.get(pk=1)
        report_flags = ReportFlag.objects.filter(
            report=self.report,
            active=True,
            removed_by_eqar=False
        )
        for report_flag in report_flags:
            if report_flag.flag.pk == 2:
                self.report.flag = Flag.objects.get(pk=2)
            if report_flag.flag.pk == 3:
                self.report.flag = Flag.objects.get(pk=3)
                break
        self.report.save()

    def check_countries(self):
        # InstitutionCountries
        for institution in self.report.institutions.all():
            for ic in institution.institutioncountry_set.filter(
                country_verified=True
            ).all():
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
                    flag_message = self.flag_msg['institutionCountry'] % (ic.country.name_english,
                                                                          self.report.agency.acronym_primary)
                    self.add_flag(flag_level=2, flag_message=flag_message)
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
                    flag_message = self.flag_msg['programmeCountry'] % (pc.name_english,
                                                                        self.report.agency.acronym_primary)
                    self.add_flag(flag_level=2, flag_message=flag_message)
                # self._check_report_status_country_is_official(afc)
                self._check_programme_country_id(pc)

    def _check_report_status_country_is_official(self, agency_focus_country):
        if self.report.status_id == 1:
            if not agency_focus_country.country_is_official:
                flag_message = self.flag_msg['statusCountryIsOfficial'] % (self.report.agency.acronym_primary,
                                                                           agency_focus_country.country.name_english)
                self.add_flag(flag_level=3, flag_message=flag_message)

    def check_report_status_country_is_official_for_multi_institution(self):
        """ for joint programme/multi-institution reports, raise a flag for lack of official status only if
        the agency has no official status in any of the institutions' legal seat countries -
        in other words: okay if they have official status in at least one of the legal seat countries"""
        if self.report.agency_esg_activity.activity_type == 3 or self.report.institutions.count() > 1:
            official_status_exists = False
            for institution in self.report.institutions.all():
                for ic in institution.institutioncountry_set.filter(country_verified=True).all():
                    if AgencyFocusCountry.objects.filter(
                            agency=self.report.agency,
                            country=ic.country,
                            country_is_official=True
                    ).exists():
                        official_status_exists = True
            if not official_status_exists:
                flag_message = self.flag_msg['statusCountryIsOfficialMultiInstitution'] % (
                    self.report.agency.acronym_primary
                )
                self.add_flag(flag_level=3, flag_message=flag_message)

    def _check_programme_country_id(self, country):
        ic_count = self.report.institutions.filter(institutioncountry__country=country).count()
        if ic_count == 0:
            flag_message = self.flag_msg['programmeCountryId'] % country
            self.add_flag(flag_level=2, flag_message=flag_message)

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
                            flag_message = self.flag_msg['programmeQFEHEALevel'] % (qf_ehea_level,
                                                                                    programme.name_primary)
                            self.add_flag(flag_level=3, flag_message=flag_message)

    def check_validity_date(self):
        if self.report.valid_to < datetime.datetime.now() - relativedelta(years=1):
            flag_message = self.flag_msg['validityDate']
            self.add_flag(flag_level=2, flag_message=flag_message)

    def check_ehea_is_member(self):
        for institution in self.report.institutions.all():
            for ic in institution.institutioncountry_set.all():
                if ic.country.ehea_is_member:
                    if institution.institutionqfehealevel_set.count() == 0:
                        flag_message = self.flag_msg['EHEAIsMember'] % (ic.institution.name_primary,
                                                                        ic.country.name_english)
                        self.add_flag(flag_level=2, flag_message=flag_message)

    def check_report_file(self):
        for rf in self.report.reportfile_set.all():
            if rf.file_original_location == "" and rf.file.name == "":
                flag_message = self.flag_msg['file']
                self.add_flag(flag_level=2, flag_message=flag_message)
