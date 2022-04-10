import json
import datetime

import requests
from datedelta import datedelta
from copy import deepcopy

from rest_framework.exceptions import APIException, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.db.models import Q

from institutions.models import InstitutionIdentifier
from reports.models import Report

class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service unavailable, try again later.'
    default_code = 'service_unavailable'


class VCIssue(APIView):
    """
    Base class for views to issue generic W3C-compliant Verifiable Credentials (VC)
    """

    # Provisional: hard-coded templates - define in subclass
    vc_template = None

    def __init__(self):
        # Get api endpoint from settings
        self.core_api = getattr(settings, "LETSTRUST_CORE_API", None)
        if not self.core_api:
            raise ServiceUnavailable(
                detail="LETSTRUST_CORE_API value is not present in the settings"
            )
        # Get EQAR DID from settings, drop error if not set
        self.eqar_did = getattr(settings, "LETSTRUST_EQAR_DID", None)
        if not self.eqar_did:
            raise ServiceUnavailable(
                detail="LETSTRUST_EQAR_DID value is not present in the settings"
            )
        # Check if template is defined
        if not self.vc_template:
            raise ServiceUnavailable(
                detail="Verifiable Credential template is not defined"
            )
        # URIs for reports, institutions and agencies
        self.report_uri = getattr(settings, "DEQAR_REPORT_URI", 'https://data.deqar.eu/report/%s')
        self.agency_uri = getattr(settings, "DEQAR_AGENCY_URI", 'https://data.deqar.eu/agency/%s')
        self.institution_uri = getattr(settings, "DEQAR_INSTITUTION_URI", 'https://data.deqar.eu/institution/%s')

    def get(self, request, *args, **kwargs):
        """
        Method handler - returns the report as one VC per institution
        """
        report_id = self.kwargs['report_id']
        report = get_object_or_404(Report, pk=report_id)

        return(self.collect_vcs(report))

    def issue_vc(self, subject_did, offer):
        """
        Issue one single VC using the Walt.ID API
        """
        post_data = {
            'issuerDid': self.eqar_did,
            'subjectDid': subject_did,
            'credentialOffer': json.dumps(offer)
        }

        api = '%s/vc/create/' % self.core_api
        r = requests.post(api, json=post_data)
        post_data['credentialOffer'] = offer
        if r.status_code != 200:
            return({'status': r.status_code, 'status_message': r.text, 'data': post_data})
        else:
            r.encoding = 'utf-8' # work-around for bug in SSIkit
            return({'status': 200, 'data': r.json()})

    def populate_vc(self, report, institution):
        """
        Use the template and populate for one institution covered by the report
        """

        # Fill the json with report data
        vc_offer = deepcopy(self.vc_template)
        vc_offer['id'] = self.report_uri % report.id
        vc_offer['issuer'] = self.eqar_did
        vc_offer['issuanceDate'] = self._translate_date(report.valid_from)
        vc_offer['validFrom'] = self._translate_date(report.valid_from)
        vc_offer['expirationDate'] = self._translate_date(report.valid_to if report.valid_to else report.valid_from + datedelta(years=6))
        vc_offer['credentialSubject']['authorizationClaims']['accreditationType'] = self._translate_activity_type(report.agency_esg_activity.activity_type)
        vc_offer['credentialSubject']['authorizationClaims']['decision'] = report.decision.decision

        # Institution ID
        vc_offer['credentialSubject']['id'] = self._translate_subject(institution)

        # official countries
        for location in institution.institutioncountry_set.filter(country_verified=True).iterator():
            vc_offer['credentialSubject']['authorizationClaims']['limitJurisdiction'].append(self._translate_country(location.country))

        # Report files
        for reportfile in report.reportfile_set.iterator():
            try:
                vc_offer['credentialSubject']['authorizationClaims']['report'].append(self.request.build_absolute_uri(reportfile.file.url))
            except (ValueError):
                pass

        if report.agency_esg_activity.activity_type.type in [ 'programme', 'joint programme' ]:
            # Programme data for programme-level reports
            vc_offer['credentialSubject']['authorizationClaims']['limitQualification'] = []
            for programme in report.programme_set.iterator():
                limitQualification = {}
                limitQualification['title'] = programme.programmename_set.filter(name_is_primary=True).first().name
                self._set_if(limitQualification, 'alternativeLabel', [ i.name for i in programme.programmename_set.filter(name_is_primary=False) ])
                self._set_if(limitQualification, 'EQFLevel', self._translate_qf_level(programme.qf_ehea_level))
                vc_offer['credentialSubject']['authorizationClaims']['limitQualification'].append(limitQualification)
        else:
            # QF levels for institutional reports
            self._set_if(vc_offer['credentialSubject']['authorizationClaims'], 'limitQFLevel', self._collect_qf_levels(institution))

        return vc_offer

    def collect_vcs(self, report):
        """
        Iterate over report institutions to populate and issue one VC per institution
        """
        post_data_log = []

        for institution in report.institutions.iterator():
            vc_offer = self.populate_vc(report, institution)
            result = self.issue_vc(None, vc_offer)
            # add additional institution data
            result["institution"] = { 'id': institution.id, 'deqar_id': institution.deqar_id, 'name_primary': institution.name_primary }
            post_data_log.append(result)

        return Response(post_data_log)

    """
    Helper functions
    """

    def _collect_qf_levels(self, institution):
        qf_levels = set()
        for level in institution.institutionqfehealevel_set.iterator():
            if self._translate_qf_level(level.qf_ehea_level):
                qf_levels.add(self._translate_qf_level(level.qf_ehea_level))
        return list(qf_levels)

    def _set_if(self, target, key, value):
        if value:
            target[key] = value
            return True
        else:
            return False

    """
    The following are meant to be overwritten in subclasses (e.g. EBSI-specific)
    """

    def _translate_subject(self, institution):
        return(self.institution_uri % institution.id)

    def _translate_activity_type(self, activity_type):
        return activity_type.type

    def _translate_country(self, country):
        return country.iso_3166_alpha3.upper()

    def _translate_qf_level(self, qf_ehea_level):
        return getattr(qf_ehea_level, 'level', None)

    def _translate_date(self, value):
        return value.strftime("%Y-%m-%dT%H:%M:%SZ") if hasattr(value, 'strftime') and callable(value.strftime) else None


class DEQARVCIssue(VCIssue):
    """
    DEQAR Verifiable Credential - proof of concept
    """

    vc_template = json.loads("""
        {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://data.deqar.eu/context/v1.jsonld"
            ],
            "id": "***",
            "type": [
                "VerifiableCredential",
                "DeqarReport"
            ],
            "issuer": "***",
            "credentialSubject": {
                "id": "***",
                "authorizationClaims": {
                    "accreditationType": "***",
                    "decision": "***",
                    "report": [ ],
                    "limitJurisdiction": [ ]
                }
            },
            "issuanceDate": "***",
            "validFrom": "***",
            "expirationDate": "***",
            "credentialSchema": {
                "id": "https://data.deqar.eu/schema/v1.json",
                "type": "JsonSchemaValidator2018"
            }
        }
    """)

    def populate_vc(self, report, institution):
        """
        Add additional data
        """
        vc_offer = super().populate_vc(report, institution)
        # report status
        vc_offer['credentialSubject']['authorizationClaims']['accreditationStatus'] = report.status.status
        vc_offer['credentialSubject']['authorizationClaims']['accreditationActivity'] = report.agency_esg_activity.activity
        # additional institution data
        vc_offer['credentialSubject']['name'] = institution.name_primary
        self._set_if(vc_offer['credentialSubject'], 'eterID', getattr(institution.eter, 'eter_id', None) )
        vc_offer['credentialSubject']['identifiers'] = []
        for identifier in institution.institutionidentifier_set.filter(agency__isnull=True):
            vc_offer['credentialSubject']['identifiers'].append({
                'identifier': identifier.identifier,
                'resource': identifier.resource
            })
        if not self._set_if(vc_offer['credentialSubject'], 'legalName', getattr(institution.institutionname_set.filter(name_valid_to=None).first(), 'name_official', None) ):
            self._set_if(vc_offer['credentialSubject'], 'legalName', getattr(institution.institutionname_set.order_by('name_valid_to').last(), 'name_official', None) )
        self._set_if(vc_offer['credentialSubject'], 'location', [ f"{l.city}, {l.country.name_english}" if l.city else l.country.name_english for l in institution.institutioncountry_set.iterator() ] )
        self._set_if(vc_offer['credentialSubject'], 'foundingDate', self._translate_date(institution.founding_date) )
        self._set_if(vc_offer['credentialSubject'], 'dissolutionDate', self._translate_date(institution.closure_date) )
        self._set_if(vc_offer['credentialSubject'], 'latitude', getattr(institution.institutioncountry_set.filter(country_verified=True).first(), 'lat', None) )
        self._set_if(vc_offer['credentialSubject'], 'longitude', getattr(institution.institutioncountry_set.filter(country_verified=True).first(), 'long', None) )
        # registered QA agency
        vc_offer['credentialSubject']['authorizationClaims']['agency'] = {
            'id': self.agency_uri % report.agency.id,
            'acronym': report.agency.acronym_primary,
            'name': report.agency.name_primary,
            'registrationValidFrom': self._translate_date(report.agency.registration_start),
            'registrationExpirationDate': self._translate_date(report.agency.registration_valid_to)
        }
        return vc_offer


class EBSIVCIssue(VCIssue):
    """
    Specific view to issue EBSI-compliant Verifiable Accreditations (Diploma Use Case)
    """

    # EBSI-specific template
    vc_template = json.loads("""
        {
            "@context": [
                "https://www.w3.org/2018/credentials/v1"
            ],
            "id": "***",
            "type": [
                "VerifiableCredential",
                "VerifiableAttestation",
                "VerifiableAccreditation",
                "DiplomaVerifiableAccreditation"
            ],
            "issuer": "***",
            "issued": "***",
            "credentialSubject": {
                "id": "***",
                "authorizationClaims": {
                    "accreditationType": "***",
                    "decision": "***",
                    "report": [ ],
                    "limitJurisdiction": [ ]
                }
            },
            "issuanceDate": "***",
            "validFrom": "***",
            "expirationDate": "***",
            "credentialSchema": {
                "id": "https://api.preprod.ebsi.eu/trusted-schemas-registry/v1/schemas/0x13d597f8495e6b6e3d0c072218756a1bcc3ea50ebeb3ab4c3944bd400e0c3c6a",
                "type": "FullJsonSchemaValidator2021"
            }
        }
    """)

    def __init__(self):
        """
        Fetch EQAR's EBSI DID from settings
        """
        super().__init__()
        # Get EQAR DID from settings, drop error if not set
        self.eqar_did = getattr(settings, "LETSTRUST_EQAR_EBSI_DID", None)
        if not self.eqar_did:
            raise ServiceUnavailable(
                detail="LETSTRUST_EQAR_EBSI_DID value is not present in the settings"
            )
        # resource tag for EBSI DID
        self.resource_did_ebsi = getattr(settings, "LETSTRUST_RESOURCE_DID_EBSI", "DID-EBSI")

    def collect_vcs(self, report):
        """
        Check status: only official reports can be issued as EBSI VC
        """
        if report.status_id != 1:
            raise NotFound(
                detail="Report is not marked as 'part of obligatory EQA system' and cannot be issued as EBSI VC."
            )
        return(super().collect_vcs(report))

    def populate_vc(self, report, institution):
        """
        Add additional data (quick fix)
        """
        vc_offer = super().populate_vc(report, institution)
        vc_offer['issued'] = vc_offer['issuanceDate']
        return(vc_offer)

    def _translate_subject(self, institution):
        """
        Get EBSI DID of the institutions mentioned in the report
        """
        institution_did = InstitutionIdentifier.objects.filter(Q(institution=institution) | Q(institution__relationship_parent__institution_child=institution), resource=self.resource_did_ebsi).first()
        if not institution_did:
            raise NotFound(
                detail="No DID-EBSI identifier found for %s (%s)" % (institution.deqar_id, institution)
            )
        return(institution_did.identifier)

    def _translate_activity_type(self, activity_type):
        """
        Translate report type to EU vocabulary
        """
        REPORT_TYPES = {
            'programme': 'http://data.europa.eu/snb/accreditation/e57dddfcf3',
            'joint programme': 'http://data.europa.eu/snb/accreditation/e57dddfcf3',
            'institutional': 'http://data.europa.eu/snb/accreditation/003293d2ce',
            'institutional/programme': 'http://data.europa.eu/snb/accreditation/003293d2ce',
        }
        return REPORT_TYPES.get(activity_type.type)

    def _translate_country(self, country):
        return f"http://publications.europa.eu/resource/authority/country/{country.iso_3166_alpha3.upper()}"

    def _translate_qf_level(self, qf_ehea_level):
        EQF_LEVELS = {
            'short cycle': 'http://data.europa.eu/snb/eqf/5',
            'first cycle': 'http://data.europa.eu/snb/eqf/6',
            'second cycle': 'http://data.europa.eu/snb/eqf/7',
            'third cycle': 'http://data.europa.eu/snb/eqf/8',
        }
        return EQF_LEVELS.get(qf_ehea_level.level, None)

