import os

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from lxml.etree import CDATA

from institutions.models import Institution
from reports.models import Report
from lxml import etree


class AccrediationXMLCreator:
    attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")

    NS = "{http://data.europa.eu/europass/qms-xml/schema/accreditation}"
    NSMAP = {
        None: 'http://data.europa.eu/europass/qms-xml/schema/accreditation',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'eup': 'http://data.europa.eu/europass/qms-xml/schema/accreditation',
    }

    REPORT_TYPES = {
        'institutional': 'http://data.europa.eu/europass/accreditationType/institutionalQualityAssurance',
        'institutional/programme': 'http://data.europa.eu/europass/accreditationType/programQualityAssurance',
        'programme': 'http://data.europa.eu/europass/accreditationType/programQualityAssurance',
        'joint programme': 'http://data.europa.eu/europass/accreditationType/programQualityAssurance'
    }

    EQF_LEVElS = {
        'short cycle': 'http://data.europa.eu/esco/eqf/5',
        'first cycle': 'http://data.europa.eu/esco/eqf/6',
        'second cycle': 'http://data.europa.eu/esco/eqf/7',
        'third cycle': 'http://data.europa.eu/esco/eqf/8',
    }

    def __init__(self, country, request):
        self.request = request
        self.country = country
        self.reports = []
        self.agencies = set()
        self.institutions = set()
        self.root = etree.Element(
            f"{self.NS}qmsAccreditations",
            {self.attr_qname: 'http://data.europa.eu/europass/qms-xml/schema/accreditation qms_accreditations.xsd'},
            nsmap=self.NSMAP,
            xsdVersion="1.1.0",
        )
        self.error = etree.Element("errors")
        self.accreditations = etree.SubElement(self.root, f"{self.NS}accreditations")
        self.agentReferences = etree.SubElement(self.root, f"{self.NS}agentReferences")
        self.scoringSchemeReferences = etree.SubElement(self.root, f"{self.NS}scoringSchemeReferences")

    def create(self):
        self.collect_reports()
        self.create_xml()
        self.add_agencies()
        self.add_institutions()
        self.create_schemas()
        return self.validate_xml()

    def collect_reports(self):
        institutions = Institution.objects.filter(
            institutioncountry__country=self.country
        )
        self.reports = Report.objects.filter(
            Q(institutions__in=institutions) &
            (Q(agency_esg_activity__activity_type=2) | Q(agency_esg_activity__activity_type=4)) &
            Q(status=1) &
            ~Q(flag=3)
        ).order_by('id').distinct('id')

    def create_xml(self):
        for report in self.reports.iterator():
            acc = etree.SubElement(self.accreditations, f"{self.NS}accreditation",
                                   id=f'https://data.deqar.eu/report/{report.id}')

            # identifier
            identifier = etree.SubElement(acc, f"{self.NS}identifier", schemeID=f'https://data.deqar.eu/report/')
            identifier.text = f'https://data.deqar.eu/report/{report.id}'

            # type
            etree.SubElement(acc, f"{self.NS}type",
                             uri=self.REPORT_TYPES[report.agency_esg_activity.activity_type.type])

            # title
            title = etree.SubElement(acc, f"{self.NS}title")
            text = etree.SubElement(title, f"{self.NS}text", attrib={'lang': 'en', 'content-type': 'text/plain'})
            text.text = report.agency_esg_activity.activity_description

            # decision
            if report.decision.id != 4:
                decision = etree.SubElement(
                    acc,
                    f"{self.NS}decision",
                    schemeID=f"https://data.deqar.eu/decision/{report.decision.decision.replace(' ', '_')}"
                )
                decision.text = report.decision.decision

            # report
            for idx, reportfile in enumerate(report.reportfile_set.iterator()):
                if idx == 0:
                    rf = etree.SubElement(
                        acc,
                        f"{self.NS}report",
                        uri=f"{self.request.build_absolute_uri(reportfile.file.url)}"
                        if reportfile.file else reportfile.file_original_location)
                    rf_title = etree.SubElement(rf, f"{self.NS}title")

                    if reportfile.file_display_name:
                        lang = reportfile.languages.first().iso_639_2 if reportfile.languages.count() > 0 else 'en'
                        rf_text = etree.SubElement(rf_title, f"{self.NS}text",
                                                   attrib={'lang': lang, 'content-type': 'text/plain'})
                        rf_text.text = reportfile.file_display_name
                    else:
                        rf_text = etree.SubElement(rf_title, f"{self.NS}text",
                                                   attrib={'lang': 'en', 'content-type': 'text/plain'})
                        rf_text.text = "quality assurance report"

                    for language in reportfile.languages.iterator():
                        etree.SubElement(
                            rf,
                            f"{self.NS}language",
                            uri=f"http://publications.europa.eu/resource/authority/language/"
                                f"{self.encode_language(language.iso_639_2)}")
                    etree.SubElement(rf, f"{self.NS}subject",
                                     uri='http://data.europa.eu/esco/qualification-topics#accreditation-and-quality-assurance')

            # organization
            institution = report.institutions.first()
            etree.SubElement(acc, f"{self.NS}organization", idref=f"https://data.deqar.eu/institution/{institution.id}")
            self.institutions.add(institution)

            # limitEQFLevel
            eqf_levels = self.collect_eqf_levels(report)
            for level in eqf_levels:
                etree.SubElement(acc, f"{self.NS}limitEQFLevel", uri=self.EQF_LEVElS[level])

            # accreditingAgent
            etree.SubElement(acc, f"{self.NS}accreditingAgent",
                             idref=f"https://data.deqar.eu/agency/{report.agency.id}")

            # issuedDate
            if report.valid_from:
                issued = etree.SubElement(acc, f"{self.NS}issuedDate")
                issued.text = report.valid_from.strftime("%Y-%m-%dT%H:%M:%S")

            # reviewDate
            review = etree.SubElement(acc, f"{self.NS}reviewDate")

            # expiryDate
            if report.valid_to:
                expiry = etree.SubElement(acc, f"{self.NS}expiryDate")
                expiry.text = report.valid_to.strftime("%Y-%m-%dT%H:%M:%S")
                review.text = report.valid_to.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                review.text = (report.valid_from + relativedelta(years=6)).strftime("%Y-%m-%dT%H:%M:%S")

            # additionalNote
            if report.other_comment:
                note = etree.SubElement(acc, f"{self.NS}additionalNote")
                note_text = etree.SubElement(note, f"{self.NS}text",
                                             attrib={'lang': 'en', 'content-type': 'text/plain'})
                note_text.text = report.other_comment

            # landingpage
            landingpage = etree.SubElement(acc, f"{self.NS}landingpage",
                                           uri=f"https://data.deqar.eu/report/{report.id}")
            hp_title = etree.SubElement(landingpage, f"{self.NS}title")
            hp_text = etree.SubElement(hp_title, f"{self.NS}text", attrib={'lang': 'en', 'content-type': 'text/plain'})
            hp_text.text = "Report on DEQAR website"
            etree.SubElement(landingpage, f"{self.NS}language",
                             uri="http://publications.europa.eu/resource/authority/language/ENG")
            etree.SubElement(landingpage, f"{self.NS}subject",
                             uri='http://data.europa.eu/esco/qualification-topics#accreditation-and-quality-assurance')

            for rl in report.reportlink_set.iterator():
                if rl.link:
                    landingpage = etree.SubElement(acc, f"{self.NS}landingpage", uri=rl.link)
                    hp_title = etree.SubElement(landingpage, f"{self.NS}title")
                    hp_text = etree.SubElement(hp_title, f"{self.NS}text",
                                               attrib={'lang': 'en', 'content-type': 'text/plain'})
                    hp_text.text = rl.link_display_name

            # supplementaryDoc
            for idx, reportfile in enumerate(report.reportfile_set.iterator()):
                if idx > 0:
                    rf = etree.SubElement(
                        acc,
                        f"{self.NS}supplementaryDoc",
                        uri=f"{self.request.build_absolute_uri(reportfile.file.url)}"
                        if reportfile.file else reportfile.file_original_location)
                    rf_title = etree.SubElement(rf, f"{self.NS}title")

                    if reportfile.file_display_name:
                        lang = reportfile.languages.first().iso_639_2 if reportfile.languages.count() > 0 else 'en'
                        rf_text = etree.SubElement(rf_title, f"{self.NS}text",
                                                   attrib={'lang': lang, 'content-type': 'text/plain'})
                        rf_text.text = reportfile.file_display_name
                    else:
                        rf_text = etree.SubElement(rf_title, f"{self.NS}text",
                                                   attrib={'lang': 'en', 'content-type': 'text/plain'})
                        rf_text.text = "quality assurance report"

                    for language in reportfile.languages.iterator():
                        etree.SubElement(
                            rf,
                            f"{self.NS}language",
                            uri=f"http://publications.europa.eu/resource/authority/language/"
                                f"{self.encode_language(language.iso_639_2)}")
                    etree.SubElement(rf, f"{self.NS}subject",
                                     uri='http://data.europa.eu/esco/qualification-topics#accreditation-and-quality-assurance')

            # status
            status = etree.SubElement(acc, f"{self.NS}status")
            status.text = "released"

            # lastModificationDate
            last_modifiation = report.reportupdatelog_set.first()
            if last_modifiation:
                last_modifiation_date = etree.SubElement(acc, f"{self.NS}lastModificationDate")
                last_modifiation_date.text = last_modifiation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")

            self.agencies.add(report.agency)

    def add_agencies(self):
        for agency in self.agencies:
            org = etree.SubElement(self.agentReferences, f"{self.NS}organization",
                                   id=f"https://data.deqar.eu/agency/{agency.id}")

            # registration
            reg = etree.SubElement(
                org,
                f"{self.NS}registration",
                spatialID=f"http://publications.europa.eu/resource/authority/country/{agency.country.iso_3166_alpha3.upper()}"
            )
            reg.text = f"https://data.deqar.eu/agency/{agency.id}"

            # identifier
            identifier = etree.SubElement(org, f"{self.NS}identifier", schemeID=f"https://data.deqar.eu/agency/")
            identifier.text = f"https://data.deqar.eu/agency/{agency.id}"

            # prefLabel and altLabel
            for agencyname in agency.agencyname_set.iterator():
                lang = agency.country.iso_3166_alpha2.lower()
                if not agencyname.name_valid_to:
                    for name_version in agencyname.agencynameversion_set.iterator():
                        preflabel = etree.SubElement(org, f"{self.NS}prefLabel")
                        preflabel_text = etree.SubElement(preflabel, f"{self.NS}text",
                                                          attrib={
                                                              'lang': self.guess_language_from_country(lang),
                                                              'content-type': 'text/plain'})
                        preflabel_text.text = f"{name_version.acronym} - {name_version.name}"
                else:
                    for name_version in agencyname.agencynameversion_set.iterator():
                        altlabel = etree.SubElement(org, f"{self.NS}altLabel")
                        altlabel_text = etree.SubElement(altlabel, f"{self.NS}text",
                                                         attrib={'lang': self.guess_language_from_country(lang),
                                                                 'content-type': 'text/plain'})
                        altlabel_text.text = f"{name_version.acronym} - {name_version.name}"

            # homepage
            etree.SubElement(org, f"{self.NS}homepage", uri=agency.website_link)

            # hasLocation
            location = etree.SubElement(org, f"{self.NS}hasLocation")
            etree.SubElement(
                location,
                f"{self.NS}spatialCode",
                uri=f"http://publications.europa.eu/resource/authority/country/{agency.country.iso_3166_alpha3.upper()}"
            )

            # contactPoint
            contact = etree.SubElement(org, f"{self.NS}contactPoint")
            address = etree.SubElement(contact, f"{self.NS}address")
            full_address = etree.SubElement(address, f"{self.NS}fullAddress")
            full_address_text = etree.SubElement(full_address, f"{self.NS}text",
                                                 attrib={'lang': 'en', 'content-type': 'text/plain'})
            full_address_text.text = CDATA(agency.address)
            etree.SubElement(
                address,
                f"{self.NS}country",
                uri=f"http://publications.europa.eu/resource/authority/country/{agency.country.iso_3166_alpha3.upper()}"
            )

            for p in agency.agencyphone_set.iterator():
                phone = etree.SubElement(contact, f"{self.NS}phone")
                phonenumber = etree.SubElement(phone, f"{self.NS}phoneNumber")
                phonenumber.text = p.phone

            for email in agency.agencyemail_set.iterator():
                etree.SubElement(contact, f"{self.NS}mailBox", uri=f"mailto:{email.email}")

            # lastModificationDate
            last_modifiation = agency.agencyupdatelog_set.first()
            if last_modifiation:
                last_modifiation_date = etree.SubElement(org, f"{self.NS}lastModificationDate")
                last_modifiation_date.text = last_modifiation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")

    def add_institutions(self):
        for institution in self.institutions:
            country = institution.institutioncountry_set.filter(country_verified=True).first()

            org = etree.SubElement(self.agentReferences, f"{self.NS}organization",
                                   id=f"https://data.deqar.eu/institution/{institution.id}")

            # identifier
            identifier = etree.SubElement(org, f"{self.NS}identifier", schemeID=f"https://data.deqar.eu/institution/")
            identifier.text = f"https://data.deqar.eu/institution/{institution.id}"

            identifier_deqar = etree.SubElement(org, f"{self.NS}identifier", schemeID=f"https://www.deqar.eu/")
            identifier_deqar.text = "DEQARINST%04d" % institution.id

            # registration
            if institution.institutionidentifier_set.filter(resource='EU-Registration').count() > 0:
                identifier = institution.institutionidentifier_set.filter(resource='EU-Registration').first()
                reg = etree.SubElement(
                    org,
                    f"{self.NS}registration",
                    spatialID=f"http://publications.europa.eu/resource/authority/country/{country.country.iso_3166_alpha3.upper()}"
                )
                reg.text = identifier.identifier
            else:
                reg = etree.SubElement(
                    org,
                    f"{self.NS}registration",
                    spatialID=f"http://publications.europa.eu/resource/authority/country/{country.country.iso_3166_alpha3.upper()}"
                )
                reg.text = f"https://data.deqar.eu/institution/{institution.id}"

            # vatIdentifier
            for identifier in institution.institutionidentifier_set.filter(resource='EU-VAT').iterator():
                vat = etree.SubElement(
                    org,
                    f"{self.NS}vatIdentifier",
                    spatialID=f"http://publications.europa.eu/resource/authority/country/{country.country.iso_3166_alpha3.upper()}"
                )
                vat.text = identifier.identifier

            # identifier
            if institution.institutionidentifier_set.filter(resource='EU-Registration').count() > 0:
                _id = etree.SubElement(
                    org,
                    f"{self.NS}identifier",
                    schemeAgencyName="DEQAR",
                    schemeID="DEQAR"
                )
                _id.text = f"https://data.deqar.eu/institution/{institution.id}"

            # ETER
            if institution.eter:
                _id = etree.SubElement(
                    org,
                    f"{self.NS}identifier",
                    schemeAgencyName="ETER",
                    schemeID="https://www.eter-project.com/"
                )
                _id.text = institution.eter.eter_id

            # prefLabel and altLabel
            for name in institution.institutionname_set.iterator():
                lang = country.country.iso_3166_alpha2.lower()
                if not name.name_valid_to:
                    preflabel = etree.SubElement(org, f"{self.NS}prefLabel")
                    preflabel_text = etree.SubElement(preflabel, f"{self.NS}text",
                                                      attrib={'lang': 'en',
                                                              'content-type': 'text/plain'})
                    if name.name_english:
                        if name.acronym:
                            preflabel_text.text = f"{name.name_english} - {name.acronym}"
                        else:
                            preflabel_text.text = f"{name.name_english}"

                        if name.name_official:
                            altlabel = etree.SubElement(org, f"{self.NS}altLabel")
                            altlabel_text = etree.SubElement(altlabel, f"{self.NS}text",
                                                             attrib={'lang': self.guess_language_from_country(lang),
                                                                     'content-type': 'text/plain'})
                            altlabel_text.text = f"{name.name_official}"
                    else:
                        if name.name_official:
                            preflabel_text = etree.SubElement(preflabel, f"{self.NS}text",
                                                             attrib={'lang': self.guess_language_from_country(lang),
                                                                     'content-type': 'text/plain'})
                            if name.acronym:
                                preflabel_text.text = f"{name.name_official} - {name.acronym}"
                            else:
                                preflabel_text.text = f"{name.name_official}"

            # homepage
            etree.SubElement(org, f"{self.NS}homepage", uri=institution.website_link)

            # hasLocation
            location = etree.SubElement(org, f"{self.NS}hasLocation")
            for country in institution.institutioncountry_set.iterator():
                etree.SubElement(
                    location,
                    f"{self.NS}spatialCode",
                    uri=f"http://publications.europa.eu/resource/authority/country/{country.country.iso_3166_alpha3.upper()}"
                )

            # lastModificationDate
            last_modifiation = institution.institutionupdatelog_set.first()
            if last_modifiation:
                last_modifiation_date = etree.SubElement(org, f"{self.NS}lastModificationDate")
                last_modifiation_date.text = last_modifiation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")

    def create_schemas(self):
        scoring_scheme = etree.SubElement(
            self.scoringSchemeReferences,
            f"{self.NS}scoringScheme",
            id="https://data.deqar.eu/decision/positive"
        )
        title = etree.SubElement(scoring_scheme, f"{self.NS}title")
        title_text = etree.SubElement(title, f"{self.NS}text", attrib={'lang': 'en', 'content-type': 'text/plain'})
        title_text.text = "positive"
        scoring_scheme = etree.SubElement(
            self.scoringSchemeReferences,
            f"{self.NS}scoringScheme",
            id="https://data.deqar.eu/decision/positive_with_conditions_or_restrictions"
        )
        title = etree.SubElement(scoring_scheme, f"{self.NS}title")
        title_text = etree.SubElement(title, f"{self.NS}text", attrib={'lang': 'en', 'content-type': 'text/plain'})
        title_text.text = "positive with conditions or restrictions"
        scoring_scheme = etree.SubElement(
            self.scoringSchemeReferences,
            f"{self.NS}scoringScheme",
            id="https://data.deqar.eu/decision/negative"
        )
        title = etree.SubElement(scoring_scheme, f"{self.NS}title")
        title_text = etree.SubElement(title, f"{self.NS}text", attrib={'lang': 'en', 'content-type': 'text/plain'})
        title_text.text = "negative"

    def validate_xml(self):
        xsd_file = os.path.join(os.getcwd(), 'connectapi/europass/qms_accreditations.xsd')
        xsd_root = etree.parse(xsd_file)
        schema = etree.XMLSchema(xsd_root)
        if not schema.validate(self.root):
            log = schema.error_log
            for log_entry in log:
                error = etree.SubElement(self.error, "error")
                error.text = str(log_entry)
            return self.error
        else:
            return self.root

    def collect_eqf_levels(self, report):
        eqf_levels = set()
        if report.agency_esg_activity.activity_type.type == 'institutional':
            for institution in report.institutions.iterator():
                for level in institution.institutionqfehealevel_set.iterator():
                    eqf_levels.add(level.qf_ehea_level.level)
        else:
            for programme in report.programme_set.iterator():
                if programme.qf_ehea_level:
                    eqf_levels.add(programme.qf_ehea_level.level)
        return eqf_levels

    def encode_language(self, language_code):
        CODES = {
            'ger': 'DEU',
            'ara': 'ENG'
        }

        if language_code in CODES:
            return CODES[language_code]
        else:
            return language_code.upper()

    def guess_language_from_country(self, country_code):
        CODES = {
            # Belgium omitted on purpose, not possible
            'bg': 'bg',
            'cz': 'cs',
            'dk': 'da',
            'at': 'de',
            'de': 'de',
            'li': 'de',
            'gr': 'el',
            'cy': 'el',
            'gb': 'en',
            'ie': 'en',
            'mt': 'en',
            'es': 'es',
            'ee': 'et',
            'fi': 'fi',
            'fr': 'fr',
            'lu': 'fr',
            'hr': 'hr',
            'hu': 'hu',
            'is': 'is',
            'it': 'it',
            'lt': 'lt',
            'lv': 'lv',
            'nl': 'nl',
            'no': 'no',
            'pl': 'pl',
            'pt': 'pt',
            'ro': 'ro',
            'sk': 'sk',
            'si': 'sl',
            'se': 'sv',
            'rs': 'sr'
        }

        if country_code in CODES:
            return CODES[country_code]
        else:
            return 'en' # default
