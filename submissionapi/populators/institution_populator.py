import datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError
from django.db.models import Q

from countries.models import Country
from institutions.models import Institution, InstitutionETERRecord, InstitutionIdentifier, InstitutionName, \
    InstitutionNameVersion, InstitutionCountry
from lists.models import QFEHEALevel
from submissionapi.flaggers.institution_flag_message_creator import InstitutionFlagMessageCreator


class InstitutionPopulator():
    """
    Class to handle the population of institution records from the submission endpoints.
    """
    def __init__(self, submission, agency):
        self.submission = submission
        self.agency = agency
        self.institution = None
        self.flag_log = []
        self.flagger = InstitutionFlagMessageCreator(agency=agency)

    def populate(self):
        self._get_institution_if_exists()

        if self.institution is not None:
            self._institution_existing_populate_identifiers()
            self._institution_existing_populate_name_english()
            self._institution_existing_populate_acronym()
            self._institution_existing_populate_name_official()
            self._institution_existing_populate_alternative_names()
            self._institution_existing_populate_locations()
            self._institution_existing_populate_qf_ehea_level()
        else:
            self._institution_create()

        self.flag_log = self.flagger.collected_flag_msg

    def _get_institution_if_exists(self):
        """
        Checks if there is a record existing with the submitted institution data.
        """
        deqar_id = self.submission.get('deqar_id', None)
        eter_id = self.submission.get('eter_id', None)
        identifiers = self.submission.get('identifiers', None)

        website_link = self.submission.get('website', None)
        name_official = self.submission.get('name_official', None)
        name_english = self.submission.get('name_english', None)

        # domain = urlparse(website_link).netloc

        if deqar_id is not None:
            try:
                self.institution = Institution.objects.get(deqar_id=deqar_id)
                return
            except ObjectDoesNotExist:
                pass

        if eter_id is not None:
            eter = None
            try:
                eter = InstitutionETERRecord.objects.get(eter_id=eter_id)
                self.institution = Institution.objects.get(eter=eter)
                return
            except ObjectDoesNotExist:
                if eter is not None:
                    self._institution_create_from_eter(eter)
                    return
                pass

        if identifiers is not None:
            for idf in identifiers:
                identifier = idf.get('identifier', None)
                resource = idf.get('resource', 'local identifier')
                try:
                    inst_id = InstitutionIdentifier.objects.get(
                        identifier=identifier,
                        resource=resource,
                        agency=self.agency
                    )
                    self.institution = inst_id.institution
                    return
                except ObjectDoesNotExist:
                    pass

        #
        # Trying to resolve institution
        #
        if website_link is not None:
            try:
                self.institution = Institution.objects.get(website_link=website_link)
                return
            except ObjectDoesNotExist:
                pass

        if name_official is not None:
            try:
                self.institution = Institution.objects.get(institutionname__name_official=name_official)
                return
            except ObjectDoesNotExist:
                pass

        if name_english is not None:
            try:
                self.institution = Institution.objects.get(institutionname__name_english=name_english)
                return
            except ObjectDoesNotExist:
                pass

        #
        # Trying to resolve ETER
        #
        if website_link is not None:
            try:
                eter = InstitutionETERRecord.objects.get(website=website_link)
                self._institution_create_from_eter(eter)
                return
            except ObjectDoesNotExist:
                pass

        if name_official is not None:
            try:
                eter = InstitutionETERRecord.objects.get(name=name_official)
                self._institution_create_from_eter(eter)
                return
            except ObjectDoesNotExist:
                pass

        if name_english is not None:
            try:
                eter = InstitutionETERRecord.objects.get(name_english=name_english)
                self._institution_create_from_eter(eter)
                return
            except ObjectDoesNotExist:
                pass

    def _institution_create(self):
        self.institution = Institution.objects.create(
            name_primary=self.submission.get('name_primary', ""),
            website_link=self.submission.get('website_link', "")
        )
        self.institution.create_deqar_id()

        identifiers = self.submission.get("identifiers", [])
        for idf in identifiers:
            resource = idf.get('resource', 'local identifier')
            if resource == 'local identifier':
                self.institution.institutionidentifier_set.create(
                    identifier=idf.get('identifier', None),
                    resource=resource,
                    agency=self.agency
                )
            else:
                self.institution.institutionidentifier_set.create(
                    identifier=idf.get('identifier', None),
                    resource=resource
                )

        inst_name_msg = "Name information supplied by [%s]." % self.agency.acronym_primary

        inst_name = self.institution.institutionname_set.create(
            name_official=self.submission.get('name_official', ""),
            name_official_transliterated=self.submission.get('name_official_transliterated', ""),
            name_english=self.submission.get('name_english', ""),
            acronym=self.submission.get('acronym', ""),
            name_source_note=inst_name_msg
        )

        alternative_names = self.submission.get("alternative_names", [])
        for alternative_name in alternative_names:
            inst_name.institutionnameversion_set.create(
                name=alternative_name.get('name_alternative', ""),
                transliteration=alternative_name.get('name_alternative_transliteration', ""),
                name_version_source='[%s]' % self.agency.acronym_primary,
            )

        locations = self.submission.get("locations", [])
        for location in locations:
            self.institution.institutioncountry_set.create(
                country=location.get("country", ""),
                city=location.get("city", ""),
                lat=location.get("latitude", None),
                long=location.get("longitude", None),
                country_source="[%s]" % self.agency.acronym_primary,
                country_valid_from=datetime.date.today()
            )

        qf_ehea_levels = self.submission.get("qf_ehea_levels", [])
        for qf_ehea_level in qf_ehea_levels:
            self.institution.institutionqfehealevel_set.create(
                qf_ehea_level=qf_ehea_level,
                qf_ehea_level_source="[%s]" % self.agency.acronym_primary,
                qf_ehea_level_valid_from=datetime.date.today()
            )
        self.institution.set_primary_name()

    def _institution_create_from_eter(self, eter):
        """
        Create Institution record from the ETER record.
        """
        name_primary = eter.name_english if len(eter.name_english) > 0 else eter.name
        self.institution = Institution.objects.create(
            eter=eter,
            website_link=eter.website,
            name_primary=name_primary
        )
        self.institution.create_deqar_id()

        self.institution.institutionidentifier_set.create(
            identifier=eter.national_identifier,
            resource='national identifier',
            identifier_valid_from=eter.valid_from_year
        )
        self.institution.institutionname_set.create(
            name_official=eter.name,
            name_english=eter.name_english,
            acronym=eter.acronym
        )
        self.institution.institutioncountry_set.create(
            country=Country.objects.get(iso_3166_alpha2=eter.country),
            city=eter.city,
            lat=eter.lat,
            long=eter.long,
            country_source="ETER",
            country_valid_from=eter.valid_from_year
        )

        isced_qf_ehea_map = {
            'ISCED 5': 0,
            'ISCED 6': 1,
            'ISCED 7': 2,
            'ISCED 8': 3
        }

        isced_lowest = eter.ISCED_lowest
        isced_highest = eter.ISCED_highest

        if isced_lowest != '' and isced_highest != '':
            for qf_ehea_code in range(isced_qf_ehea_map[isced_lowest], isced_qf_ehea_map[isced_highest]+1):
                self.institution.institutionqfehealevel_set.create(
                    qf_ehea_level=QFEHEALevel.objects.get(code=qf_ehea_code),
                    qf_ehea_level_source='ETER',
                    qf_ehea_level_valid_from=eter.valid_from_year
                )

    def _institution_existing_populate_identifiers(self):
        """
        Populate identifiers if institution exists.
        """
        identifiers = self.submission.get('identifiers', [])

        for idf in identifiers:
            identifier = idf.get('identifier', None)
            resource = idf.get('resource', 'local identifier')

            if resource == 'local identifier':
                try:
                    InstitutionIdentifier.objects.get_or_create(
                        institution=self.institution,
                        identifier=identifier,
                        resource=resource,
                        agency=self.agency
                    )
                except MultipleObjectsReturned:
                    pass
                except IntegrityError:
                    pass
            else:
                try:
                    idf_count = InstitutionIdentifier.objects.filter(
                        institution=self.institution,
                        resource=resource
                    ).count()
                    if idf_count == 0:
                        self.institution.institutionidentifier_set.create(
                            identifier=identifier,
                            resource=resource
                        )
                except MultipleObjectsReturned:
                    pass

    def _institution_existing_populate_name_english(self):
        """
        Populate name_english if institution exists.
        """
        name_english = self.submission.get('name_english', None)

        iname_primary = InstitutionName.objects.get(institution=self.institution, name_valid_to__isnull=True)
        if iname_primary.name_english == '':
            iname_primary.name_english = name_english
            iname_primary.add_source_note(self.flagger.get_message('name_english', name_english))
            self.institution.set_flag_low()
        else:
            iname_ver_count = InstitutionNameVersion.objects.filter(
                Q(institution_name=iname_primary) & Q(name=name_english)
            ).count()
            if iname_ver_count == 0:
                InstitutionNameVersion.objects.create(
                    institution_name=iname_primary,
                    name=name_english,
                    name_version_source=self.agency.acronym_primary,
                    name_version_source_note=self.flagger.get_message('name_alternative', name_english)
                )
                self.institution.set_flag_low()

    def _institution_existing_populate_acronym(self):
        """
        Populate acronym if institution exists.
        """
        acronym = self.submission.get('acronym', None)

        iname_primary = InstitutionName.objects.get(institution=self.institution, name_valid_to__isnull=True)
        if iname_primary.acronym == '':
            iname_primary.acronym = acronym
            iname_primary.add_source_note(self.flagger.get_message('acronym', acronym))
            self.institution.set_flag_low()

        else:
            if iname_primary.acronym != acronym:
                iname_primary.add_source_note(self.flagger.get_message('acronym', acronym))
                self.institution.set_flag_low()

    def _institution_existing_populate_name_official(self):
        """
        Populate name_official if institution exists.
        """
        name_official = self.submission.get('name_official', "")
        name_official_transliterated = self.submission.get('name_official_transliterated', "")

        iname_primary = InstitutionName.objects.get(institution=self.institution, name_valid_to__isnull=True)

        iname = InstitutionName.objects.filter(
            Q(institution=self.institution) &
            (Q(name_official=name_official) | Q(name_official_transliterated=name_official))
        ).count()

        if iname == 0:
            iname_ver_count = InstitutionNameVersion.objects.filter(
                Q(institution_name__institution=self.institution) &
                (Q(name=name_official) | Q(transliteration=name_official))
            ).count()
            if iname_ver_count == 0:
                InstitutionNameVersion.objects.create(
                    institution_name=iname_primary,
                    name=name_official,
                    transliteration=name_official_transliterated,
                )
            iname_primary.add_source_note(self.flagger.get_message('name_official', name_official))
            self.institution.set_flag_low()

    def _institution_existing_populate_alternative_names(self):
        """
        Populate alternative_names if institution exists.
        """
        alternative_names = self.submission.get('alternative_names', [])

        for alternative_name in alternative_names:
            name_alternative = alternative_name.get('name_alternative', "")
            name_alternative_transliterated = alternative_name.get('name_alternative_transliterated', "")

            iname_count = InstitutionName.objects.filter(
                Q(institution=self.institution) &
                (Q(name_official=name_alternative) | Q(name_official_transliterated=name_alternative))
            ).count()

            iname_ver_count = InstitutionNameVersion.objects.filter(
                Q(institution_name__institution=self.institution) &
                (Q(name=name_alternative) | Q(transliteration=name_alternative))
            ).count()

            if iname_count == 0 and iname_ver_count == 0:
                iname_primary = InstitutionName.objects.get(institution=self.institution, name_valid_to__isnull=True)
                InstitutionNameVersion.objects.create(
                    institution_name=iname_primary,
                    name=name_alternative,
                    transliteration=name_alternative_transliterated,
                    name_version_source=self.agency.acronym_primary,
                    name_version_source_note=self.flagger.get_message('alternative_name', name_alternative)
                )

    def _institution_existing_populate_locations(self):
        locations = self.submission.get('locations', [])

        for location in locations:
            country = location.get('country', None)
            city = location.get('city', None)
            latitude = location.get('latitude', None)
            longitude = location.get('longitude', None)

            try:
                ic = InstitutionCountry.objects.get(
                    institution=self.institution,
                    country=country
                )
                if ic.city == city:
                    if ic.lat is None:
                        ic.lat = latitude
                        ic.long = longitude
                if ic.city != "" and ic.city != city:
                    ic.add_source_note(self.flagger.get_message('city', city))
                    self.institution.set_flag_low()
                if ic.city == "":
                    ic.city = city
                    ic.lat = latitude
                    ic.long = longitude
                ic.save()
            except ObjectDoesNotExist:
                ic = self.institution.institutioncountry_set.create(
                    country=country,
                    city=city,
                    lat=latitude,
                    long=longitude,
                    country_verified=False,
                )
                ic.add_source_note(self.flagger.get_message('country', country))
                self.institution.set_flag_low()

    def _institution_existing_populate_qf_ehea_level(self):
        qf_ehea_levels = self.submission.get("qf_ehea_levels", [])

        for qfe in qf_ehea_levels:
            inst_qf_ehea_count = self.institution.institutionqfehealevel_set.count()
            if inst_qf_ehea_count == 0:
                self.institution.institutionqfehealevel_set.create(
                    qf_ehea_level=qfe,
                    qf_ehea_level_source=self.agency.acronym_primary,
                    qf_ehea_level_valid_from=datetime.date.today()
                )
            else:
                inst_qf_ehea_include = self.institution.institutionqfehealevel_set.filter(
                    qf_ehea_level=qfe
                ).count()
                if inst_qf_ehea_include == 0:
                    self.institution.institutionqfehealevel_set.create(
                        qf_ehea_level=qfe,
                        qf_ehea_level_source=self.agency.acronym_primary,
                        qf_ehea_level_source_note=self.flagger.get_message('qf_ehea_level', qfe),
                        qf_ehea_level_valid_from=datetime.date.today(),
                        qf_ehea_level_verified=False
                    )
                    self.institution.set_flag_low()
