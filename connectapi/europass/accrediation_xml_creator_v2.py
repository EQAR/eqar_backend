import os

from django.core.exceptions import ObjectDoesNotExist
from langdetect import detect
from dateutil.relativedelta import relativedelta
from django.db.models import Q

from agencies.models import Agency
from countries.models import Country
from institutions.models import Institution, InstitutionHierarchicalRelationship
from reports.models import Report
from lxml import etree


class AccrediationXMLCreatorV2:
    attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")

    NS = "{http://data.europa.eu/snb/model/ap/ams-constraints/}"
    NSMAP = {
        'skos': 'http://www.w3.org/2004/02/skos/core#',
        'clv': 'http://data.europa.eu/m8g/',
        None: 'http://data.europa.eu/snb/model/ap/ams-constraints/',
        'dc': 'http://purl.org/dc/terms/',
        'locn': 'http://www.w3.org/ns/locn#'
    }

    REPORT_TYPES = {
        'institutional': 'http://data.europa.eu/snb/accreditation/003293d2ce',
        'institutional/programme': 'http://data.europa.eu/snb/accreditation/003293d2ce',
        'programme': 'http://data.europa.eu/snb/accreditation/e57dddfcf3',
        'joint programme': 'http://data.europa.eu/snb/accreditation/e57dddfcf3'
    }

    EQF_LEVElS = {
        'short cycle': 'http://data.europa.eu/snb/eqf/5',
        'first cycle': 'http://data.europa.eu/snb/eqf/6',
        'second cycle': 'http://data.europa.eu/snb/eqf/7',
        'third cycle': 'http://data.europa.eu/snb/eqf/8',
    }

    def __init__(self, country, request):
        self.request = request
        self.country = country
        self.reports = []
        self.agencies = set()
        self.institutions = set()
        self.agency_countries = set()
        self.locations = set()
        self.root = etree.Element(
            f"{self.NS}Accreditations",
            {self.attr_qname: 'http://data.europa.eu/snb/model/ap/ams-constraints/ ams.xsd'},
            nsmap=self.NSMAP,
            xsdVersion="3.0.0",
        )
        self.error = etree.Element("errors")

        self.current_report = None

        self.accreditations = etree.SubElement(self.root, f"{self.NS}accreditationReferences")
        self.orgReferences = etree.SubElement(self.root, f"{self.NS}agentReferences")
        self.locationReferences = etree.SubElement(self.root, f"{self.NS}locationReferences")

    def create(self):
        self.collect_reports()
        self.create_xml()
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
        for report in self.reports:
            self.current_report = report
            # Prepare list for agencies
            self.agencies.add(report.agency_id)

            # Prepare list for institutions
            for institution in report.institutions.iterator():
                self.institutions.add(institution.id)

                # Add child institutions
                for ih in InstitutionHierarchicalRelationship.objects.filter(
                    institution_parent=institution,
                ).exclude(relationship_type=1).all():
                    self.institutions.add(ih.institution_child_id)

                # Add parent institutions
                for ih in InstitutionHierarchicalRelationship.objects.filter(
                    institution_child=institution
                ).exclude(relationship_type=1).all():
                    self.institutions.add(ih.institution_parent_id)

            # Create accreditation records
            self.add_accreditation()

        # Create orgs and organisations
        self.add_agencies()
        self.add_location_from_agencies()
        self.add_institutions()

    def add_accreditation(self):
            acc = etree.SubElement(self.accreditations, f"{self.NS}accreditation",
                                   id=f'https://data.deqar.eu/report/{self.current_report.id}')

            # identifier
            identifier = etree.SubElement(acc, f"{self.NS}identifier")
            scheme_id = etree.SubElement(identifier, f"{{http://www.w3.org/2004/02/skos/core#}}notation")
            scheme_id.text = f'https://data.deqar.eu/report/{self.current_report.id}'
            dc_creator = etree.SubElement(identifier, f"{{http://purl.org/dc/terms/}}creator")
            dc_creator.text = 'https://deqar.eu/'
            scheme_agency = etree.SubElement(identifier, f"{self.NS}schemeAgency", attrib={'language': 'en'})
            scheme_agency.text = 'https://deqar.eu/'
            issued = etree.SubElement(identifier, f"{self.NS}issued")
            issued.text = self.current_report.created_at.strftime("%Y-%m-%dT%H:%M:%S")

            # type
            etree.SubElement(acc, f"{self.NS}type",
                             uri=self.REPORT_TYPES[self.current_report.agency_esg_activity.activity_type.type])

            # title
            title = etree.SubElement(acc, f"{self.NS}title", attrib={'language': 'en'})
            title.text = self.current_report.agency_esg_activity.activity_description

            # decision
            if self.current_report.decision.id != 4:
                decision = etree.SubElement(
                    acc,
                    f"{self.NS}decision",
                    attrib={'uri': f"https://data.deqar.eu/decision/{self.current_report.decision.decision.replace(' ', '_')}"}
                )
                pref_label = etree.SubElement(
                    decision,
                    f"{{http://www.w3.org/2004/02/skos/core#}}prefLabel",
                    attrib={'language': 'en'})
                pref_label.text = self.current_report.decision.decision

            # report
            for idx, reportfile in enumerate(self.current_report.reportfile_set.iterator()):
                if idx == 0:
                    if reportfile.file or reportfile.file_original_location:
                        rf = etree.SubElement(acc, f"{self.NS}report")

                        if reportfile.file_display_name:
                            lang = reportfile.languages.first().iso_639_1 if reportfile.languages.count() > 0 else 'en'
                            rf_title = etree.SubElement(
                                rf,
                                f"{self.NS}title",
                                attrib={'language': lang})
                            rf_title.text = reportfile.file_display_name
                        else:
                            rf_title = etree.SubElement(
                                rf,
                                f"{self.NS}title",
                                attrib={'language': 'en'})
                            rf_title.text = "quality assurance report"

                        for language in reportfile.languages.iterator():
                            etree.SubElement(
                                rf,
                                f"{self.NS}language",
                                uri=f"http://publications.europa.eu/resource/authority/language/"
                                    f"{self.encode_language(language.iso_639_2)}")

                        if reportfile.file:
                            content_url = etree.SubElement(rf, f"{self.NS}contentUrl")
                            content_url.text = f"{self.request.build_absolute_uri(reportfile.file.url)}"
                        else:
                            content_url = etree.SubElement(rf, f"{self.NS}contentUrl")
                            content_url.text = f"{self.request.build_absolute_uri(reportfile.file_original_location)}"

            # organisation
            for institution in self.current_report.institutions.all():
                etree.SubElement(acc, f"{self.NS}organisation", idref=f"https://data.deqar.eu/institution/{institution.id}")

            # limitEQFLevel
            eqf_levels = self.collect_eqf_levels(self.current_report)
            for level in eqf_levels:
                etree.SubElement(acc, f"{self.NS}limitEQFLevel", uri=self.EQF_LEVElS[level])

            # accreditingAgent
            etree.SubElement(acc, f"{self.NS}accreditingAgent",
                             idref=f"https://data.deqar.eu/agency/{self.current_report.agency.id}")

            # issued
            if self.current_report.valid_from:
                issued = etree.SubElement(acc, f"{self.NS}issued")
                issued.text = self.current_report.valid_from.strftime("%Y-%m-%dT%H:%M:%S")

            # reviewDate
            review = etree.SubElement(acc, f"{self.NS}reviewDate")

            # expiryDate
            if self.current_report.valid_to:
                expiry = etree.SubElement(acc, f"{self.NS}expiryDate")
                expiry.text = self.current_report.valid_to.strftime("%Y-%m-%dT%H:%M:%S")
                review.text = self.current_report.valid_to.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                review.text = (self.current_report.valid_from + relativedelta(years=6)).strftime("%Y-%m-%dT%H:%M:%S")

            # additionalNote
            if self.current_report.other_comment:
                note = etree.SubElement(acc, f"{self.NS}additionalNote")
                note_text = etree.SubElement(note, f"{self.NS}noteLiteral", attrib={'language': 'en'})
                note_text.text = self.current_report.other_comment

            # landingpage
            landing_page = etree.SubElement(acc, f"{self.NS}landingPage")
            lp_title = etree.SubElement(landing_page, f"{self.NS}title", attrib={'language': 'en'})
            lp_title.text = "Report on DEQAR website"

            etree.SubElement(landing_page, f"{self.NS}language",
                             uri="http://publications.europa.eu/resource/authority/language/ENG")

            content_url = etree.SubElement(landing_page, f"{self.NS}contentUrl")
            content_url.text = f"https://data.deqar.eu/report/{self.current_report.id}"

            for rl in self.current_report.reportlink_set.iterator():
                if rl.link:
                    landing_page = etree.SubElement(acc, f"{self.NS}landingPage")
                    lp_title = etree.SubElement(landing_page, f"{self.NS}title", attrib={'language': 'en'})
                    lp_title.text = rl.link_display_name

                    content_url = etree.SubElement(landing_page, f"{self.NS}contentUrl")
                    content_url.text = rl.link

            # supplementaryDocument
            for idx, reportfile in enumerate(self.current_report.reportfile_set.iterator()):
                if idx > 0:
                    if reportfile.file or reportfile.file_original_location:
                        rf = etree.SubElement(acc, f"{self.NS}supplementaryDocument")

                        if reportfile.file_display_name:
                            lang = reportfile.languages.first().iso_639_1 if reportfile.languages.count() > 0 else 'en'
                            rf_title = etree.SubElement(rf, f"{self.NS}title", attrib={'language': lang})
                            rf_title.text = reportfile.file_display_name
                        else:
                            rf_title = etree.SubElement(rf, f"{self.NS}title", attrib={'language': 'en'})
                            rf_title.text = "quality assurance report"

                        content_url = etree.SubElement(rf, f"{self.NS}contentUrl")
                        if reportfile.file:
                            content_url.text = self.request.build_absolute_uri(reportfile.file.url)
                        else:
                            content_url.text = reportfile.file_original_location

            # status
            status = etree.SubElement(acc, f"{self.NS}status")
            status.text = "released"

            # lastModificationDate
            last_modifiation = self.current_report.reportupdatelog_set.first()
            modified = etree.SubElement(acc, f"{self.NS}modified")
            if last_modifiation:
                modified.text = last_modifiation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                modified.text = self.current_report.updated_at.strftime("%Y-%m-%dT%H:%M:%S")

    def add_agencies(self):
        for agency in Agency.objects.filter(pk__in=self.agencies).all():
            org = etree.SubElement(self.orgReferences, f"{self.NS}organisation",
                                   id=f"https://data.deqar.eu/agency/{agency.id}")

            # legal name
            legalname = etree.SubElement(
                org,
                f"{self.NS}legalName",
                attrib={
                    'language': 'en'
                })
            legalname.text = f"{agency.acronym_primary} - {agency.name_primary}"

            # identifier
            identifier = etree.SubElement(org, f"{self.NS}identifier")

            notation = etree.SubElement(identifier, f"{{http://www.w3.org/2004/02/skos/core#}}notation")
            notation.text = f"https://data.deqar.eu/agency/{agency.id}"

            scheme_agency = etree.SubElement(identifier, f"{self.NS}schemeAgency", attrib={'language': 'en'})
            scheme_agency.text = 'DEQAR'

            # homepage
            if agency.website_link:
                homepage = etree.SubElement(org, f"{self.NS}homepage")
                content_url = etree.SubElement(homepage, f"{self.NS}contentUrl")
                content_url.text = agency.website_link

            # additionalNote
                # additionalNote
                for agencyname in agency.agencyname_set.iterator():
                    for name_version in agencyname.agencynameversion_set.iterator():
                        if agency.name_primary != name_version.name:
                            note = etree.SubElement(org, f"{self.NS}additionalNote")
                            subject = etree.SubElement(
                                note,
                                f"{{http://purl.org/dc/terms/}}subject",
                                attrib={'uri': 'https://data.deqar.eu/subject/#agency-alternative-name'}
                            )
                            pref_label = etree.SubElement(
                                subject,
                                f"{{http://www.w3.org/2004/02/skos/core#}}prefLabel",
                                attrib={'language': 'en'}
                            )
                            pref_label.text = "Agency Alternative Name"
                            note_literal = etree.SubElement(
                                note,
                                f"{self.NS}noteLiteral",
                                attrib={'language': self.guess_language_from_string(name_version.name)})
                            if name_version.acronym:
                                note_literal.text = f"{name_version.acronym} - {name_version.name}"
                            else:
                                note_literal.text = f"{name_version.name}"

            # location
            etree.SubElement(
                org,
                f"{self.NS}location",
                attrib={'idref': f"https://data.deqar.eu/agency-location/{agency.country.iso_3166_alpha3}"}
            )
            self.agency_countries.add(agency.country.id)

            # contactPoint
            contact = etree.SubElement(org, f"{self.NS}contactPoint")
            address = etree.SubElement(contact, f"{self.NS}address")
            full_address = etree.SubElement(address, f"{self.NS}fullAddress")
            full_address_text = etree.SubElement(
                full_address,
                f"{self.NS}noteLiteral",
                attrib={'language': 'en'})
            full_address_text.text = agency.address
            etree.SubElement(
                address,
                f"{self.NS}countryCode",
                uri=self.get_eu_controlled_vocab_country(agency.country)
            )

            for p in agency.agencyphone_set.iterator():
                phone = etree.SubElement(contact, f"{self.NS}phone")
                phonenumber = etree.SubElement(phone, f"{self.NS}phoneNumber")
                phonenumber.text = p.phone

            for email in agency.agencyemail_set.iterator():
                mailbox = etree.SubElement(contact, f"{self.NS}emailAddress")
                mailbox.text = f"mailto:{email.email}"

            # modified
            last_modifiation = agency.agencyupdatelog_set.first()
            last_modifiation_date = etree.SubElement(org, f"{self.NS}modified")
            if last_modifiation:
                last_modifiation_date.text = last_modifiation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                last_modifiation_date.text = agency.created_at.strftime("%Y-%m-%dT%H:%M:%S")

    def add_institutions(self):
        for institution in Institution.objects.filter(pk__in=self.institutions).all():
            self.assemble_institution(institution)

    def assemble_institution(self, institution, parent_of=None, child_of=None):
            country = institution.institutioncountry_set.filter(country_verified=True).first()
            org = etree.SubElement(self.orgReferences, f"{self.NS}organisation",
                                   id=f"https://data.deqar.eu/institution/{institution.id}")

            # legal name
            legalname = etree.SubElement(
                org,
                f"{self.NS}legalName",
                attrib={
                    'language': 'en'
                })
            legalname.text = f"{institution.name_primary}"

            # identifiers
            _id = etree.SubElement(
                org,
                f"{self.NS}identifier",
            )
            notation = etree.SubElement(_id, f"{{http://www.w3.org/2004/02/skos/core#}}notation")
            notation.text = f"https://data.deqar.eu/institution/{institution.id}"
            scheme_agency = etree.SubElement(_id, f"{self.NS}schemeAgency", attrib={'language': 'en'})
            scheme_agency.text = "DEQAR"

            # ETER
            if institution.eter_id:
                _id = etree.SubElement(
                    org,
                    f"{self.NS}identifier",
                )
                notation = etree.SubElement(_id, f"{{http://www.w3.org/2004/02/skos/core#}}notation")
                notation.text = institution.eter_id
                scheme_agency = etree.SubElement(_id, f"{self.NS}schemeAgency", attrib={'language': 'en'})
                scheme_agency.text = "ETER"

            # DEQARINST
            _id = etree.SubElement(
                org,
                f"{self.NS}identifier",
            )
            notation = etree.SubElement(_id, f"{{http://www.w3.org/2004/02/skos/core#}}notation")
            notation.text = "DEQARINST%04d" % institution.id
            scheme_agency = etree.SubElement(_id, f"{self.NS}schemeAgency", attrib={'language': 'en'})
            scheme_agency.text = "DEQAR"

            # registration
            if institution.institutionidentifier_set.filter(resource='EU-Registration').count() > 0:
                for identifier in institution.institutionidentifier_set.filter(resource='EU-Registration').all():
                    reg = etree.SubElement(org, f"{self.NS}registration")
                    notation = etree.SubElement(reg, f"{{http://www.w3.org/2004/02/skos/core#}}notation")
                    notation.text = identifier.identifier
                    etree.SubElement(
                        reg,
                        f"{self.NS}spatial",
                        attrib={'uri': self.get_eu_controlled_vocab_country(country.country)}
                    )

            # vatIdentifier
            for identifier in institution.institutionidentifier_set.filter(resource='EU-VAT').iterator():
                vat = etree.SubElement(
                    org,
                    f"{self.NS}vatIdentifier"
                )
                notation = etree.SubElement(vat, f"{{http://www.w3.org/2004/02/skos/core#}}notation")
                notation.text = identifier.identifier
                etree.SubElement(
                    vat,
                    f"{self.NS}spatial",
                    attrib={'uri': self.get_eu_controlled_vocab_country(country.country)}
                )

            # homepage
            if institution.website_link:
                homepage = etree.SubElement(org, f"{self.NS}homepage")
                content_url = etree.SubElement(homepage, f"{self.NS}contentUrl")
                content_url.text = institution.website_link

            # additionalNote
            for name in institution.institutionname_set.iterator():
                if name.name_english:
                    if institution.name_primary != name.name_english:
                        note = etree.SubElement(org, f"{self.NS}additionalNote")
                        subject = etree.SubElement(
                            note,
                            f"{{http://purl.org/dc/terms/}}subject",
                            attrib={'uri': 'https://data.deqar.eu/subject/#institution-alternative-name'}
                        )
                        pref_label = etree.SubElement(
                            subject,
                            f"{{http://www.w3.org/2004/02/skos/core#}}prefLabel",
                            attrib={'language': 'en'}
                        )
                        pref_label.text = "Institution Alternative Name"
                        note_literal = etree.SubElement(
                            note,
                            f"{self.NS}noteLiteral",
                            attrib={'language': 'en'})
                        if name.acronym:
                            note_literal.text = f"{name.name_english} - {name.acronym}"
                        else:
                            note_literal.text = f"{name.name_english}"

                if name.name_official:
                    if institution.name_primary != name.name_official:
                        note = etree.SubElement(org, f"{self.NS}additionalNote")
                        subject = etree.SubElement(
                            note,
                            f"{{http://purl.org/dc/terms/}}subject",
                            attrib={'uri': 'https://data.deqar.eu/subject/#institution-alternative-name'}
                        )
                        pref_label = etree.SubElement(
                            subject,
                            f"{{http://www.w3.org/2004/02/skos/core#}}prefLabel",
                            attrib={'language': 'en'}
                        )
                        pref_label.text = "Institution Alternative Name"
                        note_literal = etree.SubElement(
                            note,
                            f"{self.NS}noteLiteral",
                            attrib={'language': self.guess_language_from_string(name.name_official)})
                        if name.acronym:
                            note_literal.text = f"{name.name_official} - {name.name_official}"
                        else:
                            note_literal.text = f"{name.name_official}"

            # location
            for ic in institution.institutioncountry_set.iterator():
                etree.SubElement(
                    org,
                    f"{self.NS}location",
                    attrib={'idref': f"https://data.deqar.eu/institution-location/{ic.id}"}
                )
                self.add_location_from_institution(ic)

            # hasSubOrganization
            try:
                for ih in InstitutionHierarchicalRelationship.objects.filter(
                    institution_parent=institution
                ).exclude(relationship_type=1).all():
                    etree.SubElement(
                        org,
                        f"{self.NS}hasSubOrganization",
                        attrib={'idref': f"https://data.deqar.eu/institution/{ih.institution_child_id}"}
                    )
            except ObjectDoesNotExist:
                pass

            # subOrganizationOf
            ih = InstitutionHierarchicalRelationship.objects.filter(
                institution_child=institution
            ).exclude(relationship_type=1).first()
            if ih:
                etree.SubElement(
                    org,
                    f"{self.NS}subOrganizationOf",
                    attrib={'idref': f"https://data.deqar.eu/institution/{ih.institution_parent_id}"}
                )

            # lastModificationDate
            last_modifiation = institution.institutionupdatelog_set.first()
            if last_modifiation:
                last_modifiation_date = etree.SubElement(org, f"{self.NS}modified")
                last_modifiation_date.text = last_modifiation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                last_modifiation_date = etree.SubElement(org, f"{self.NS}modified")
                last_modifiation_date.text = institution.created_at.strftime("%Y-%m-%dT%H:%M:%S")

    def add_location_from_agencies(self):
        for country in Country.objects.filter(pk__in=self.agency_countries).all():
            location = etree.SubElement(
                self.locationReferences,
                f"{self.NS}location",
                attrib={'id': f"https://data.deqar.eu/agency-location/{country.iso_3166_alpha3}"}
            )
            geographic_name = etree.SubElement(
                location,
                f"{self.NS}geographicName",
                attrib={'language': 'en'}
            )
            geographic_name.text = country.name_english
            etree.SubElement(
                location,
                f"{self.NS}spatialCode",
                attrib={'uri': self.get_eu_controlled_vocab_country(country)}
            )
            address = etree.SubElement(location, f"{self.NS}address")
            etree.SubElement(
                address,
                f"{self.NS}countryCode",
                attrib={'uri': self.get_eu_controlled_vocab_country(country)}
            )
    def add_location_from_institution(self, ic):
        location = etree.SubElement(
            self.locationReferences,
            f"{self.NS}location",
            attrib={'id': f"https://data.deqar.eu/institution-location/{ic.id}"}
        )
        geographic_name = etree.SubElement(
            location,
            f"{self.NS}geographicName",
            attrib={'language': 'en'}
        )
        geographic_name.text = ic.country.name_english
        etree.SubElement(
            location,
            f"{self.NS}spatialCode",
            attrib={'uri': self.get_eu_controlled_vocab_country(ic.country)}
        )

        address = etree.SubElement(location, f"{self.NS}address")
        full_address = etree.SubElement(address, f"{self.NS}fullAddress")
        full_address_text = etree.SubElement(
            full_address,
            f"{self.NS}noteLiteral",
            attrib={'language': 'en'})
        full_address_text.text = ic.city
        etree.SubElement(
            address,
            f"{self.NS}countryCode",
            attrib={'uri': self.get_eu_controlled_vocab_country(ic.country)}
        )

        if ic.long or ic.lat:
            geometry = etree.SubElement(location, f"{{http://www.w3.org/ns/locn#}}geometry")
            long = etree.SubElement(geometry, f"{{http://data.europa.eu/m8g/}}longitude")
            long.text = str(ic.long)
            long = etree.SubElement(geometry, f"{{http://data.europa.eu/m8g/}}latitude")
            long.text = str(ic.lat)

    def validate_xml(self):
        if self.request.query_params.get('check', '') == 'false':
            return self.root
        else:
            xsd_file = os.path.join(os.getcwd(), 'connectapi/europass/schema/ams.xsd')
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
            'ara': 'ENG',
            'fre': 'FRA'
        }

        if language_code in CODES:
            return CODES[language_code]
        else:
            return language_code.upper()


    def guess_language_from_string(self, string):
        return detect(string)

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
            return 'en'

    def get_eu_controlled_vocab_country(self, country):
        if country.eu_controlled_vocab_country:
            return country.eu_controlled_vocab_country
        else:
            return country.parent.eu_controlled_vocab_country
