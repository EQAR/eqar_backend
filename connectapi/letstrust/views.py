import json
import datetime

import requests
from datedelta import datedelta
from copy import deepcopy
from collections import defaultdict

from rest_framework.exceptions import APIException, NotFound, NotAcceptable
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
import rest_framework.renderers
from django.conf import settings
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

from institutions.models import InstitutionIdentifier
from reports.models import Report
from connectapi.renderers import JWTRenderer

class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service unavailable, try again later.'
    default_code = 'service_unavailable'


class VCIssue(APIView):
    """
    Base class for views to issue generic W3C-compliant Verifiable Credentials (VC)
    """
    renderer_classes = [
        rest_framework.renderers.JSONRenderer,
        rest_framework.renderers.BrowsableAPIRenderer,
        JWTRenderer,
    ]
    pagination_class = None

    # VC template (override in subclass)
    vc_template = None

    # mapping from file extensions to proof types
    prooftypes = {
        'api': 'LD_PROOF',
        'json': 'LD_PROOF',
        'jwt': 'JWT'
    }

    def __init__(self):
        # Get api endpoint from settings
        self.signatory_api = getattr(settings, "LETSTRUST_SIGNATORY_API", None)
        if not self.signatory_api:
            raise ServiceUnavailable(
                detail="LETSTRUST_SIGNATORY_API value is not present in the settings"
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
        self.vc_uri = getattr(settings, "DEQAR_VC_URI", 'https://data.deqar.eu/vc/%s/%s')
        self.report_uri = getattr(settings, "DEQAR_REPORT_URI", 'https://data.deqar.eu/report/%s')
        self.agency_uri = getattr(settings, "DEQAR_AGENCY_URI", 'https://data.deqar.eu/agency/%s')
        self.institution_uri = getattr(settings, "DEQAR_INSTITUTION_URI", 'https://data.deqar.eu/institution/%s')
        self.institution_identifier_uri = getattr(settings, "DEQAR_INSTITUTION_IDENTIFIER_URI", 'https://data.deqar.eu/institution-identifier/%s')
        self.programme_uri = getattr(settings, "DEQAR_PROGRAMME_URI", 'https://data.deqar.eu/programme/%s')
        self.country_uri = getattr(settings, "DEQAR_COUNTRY_URI", 'https://data.deqar.eu/country/%s')

    def get(self, request, report_id, *args, **kwargs):
        """
        Method handler - returns the report as VC
        """
        if request.accepted_renderer.format not in self.prooftypes:
            raise NotAcceptable(
                detail="No proof type mapped for format '%s'" % request.accepted_renderer.format
            )
        else:
            prooftype = self.prooftypes.get(request.accepted_renderer.format)
        # get report and institution objects
        report = get_object_or_404(Report, pk=report_id)
        # call issuer
        return self.issue_vc(report, prooftype)

    def issue_vc(self, report, prooftype):
        """
        Issue one single VC using the Walt.ID API
        """
        # TO DO: change back to using compose_vc() when SSIkit supports multi-subject VCs
        vc_data = self.compose_vc(report)
        # compose request to SSIkit Signatory API
        post_data = {
            'templateId': self.vc_template,
            'config': self.configure_vc(report, institution, prooftype),
            'credentialData': vc_data
        }
        api = '%s/credentials/issueFromJson' % self.signatory_api
        r = requests.post(api, json=vc_data)
        if r.status_code == 200:
            if prooftype == 'JWT':
                return Response(r.text)
            else:
                return Response(r.json())
        else:
            response = { 'status': r.status_code, 'post_data': post_data }
            try:
                response['status_details'] = r.json()
            except json.decoder.JSONDecodeError:
                response['status_details'] = r.text
            return Response(response, status=r.status_code)

    def configure_vc(self, report, institution, prooftype):
        """
        Generate config object for VC issue request
        """
        return {
            'issuerDid': self.eqar_did,
            'subjectDid': self._translate_subject(institution),
            'proofType': prooftype,
            #'domain': 'data.deqar.eu',
            #'nonce': '4711',
            #'proofPurpose': 'xyz',
            'credentialId': self._translate_vc(report, institution),
            'issueDate': self._translate_date(report.valid_from),
            'validDate': self._translate_date(report.valid_from),
            'expirationDate': self._translate_date(report.valid_to if report.valid_to else report.valid_from + datedelta(years=6)),
            #'ldSignatureType': '',
            #'ecosystem': 'DEFAULT'
        }

    def populate_vc(self, report):
        """
        Use the template and populate VC
        """
        vc_data = defaultdict(dict)
        vc_data['id'] = self.report_uri % report.id
        vc_data['issuer'] = self.eqar_did
        vc_data['issuanceDate'] = self._translate_date(report.valid_from)
        vc_data['validFrom'] = self._translate_date(report.valid_from)
        vc_data['expirationDate'] = self._translate_date(report.valid_to if report.valid_to else report.valid_from + datedelta(years=6))

        # Template with institution-independent data
        vc_data['credentialSubject']['authorizationClaims'] = {
            'accreditationType': self._translate_activity_type(report.agency_esg_activity.activity_type),
            'decision': report.decision.decision,
            'report': []
        }
        for reportfile in report.reportfile_set.iterator():
            try:
                vc_data['credentialSubject']['authorizationClaims']['report'].append(self.request.build_absolute_uri(reportfile.file.url))
            except (ValueError):
                pass
        if report.agency_esg_activity.activity_type.type in [ 'programme', 'joint programme' ]:
            # Programme data for programme-level reports
            vc_data['credentialSubject']['authorizationClaims']['limitQualification'] = []
            for programme in report.programme_set.iterator():
                limitQualification = {}
                limitQualification['title'] = programme.programmename_set.filter(name_is_primary=True).first().name
                self._set_if(limitQualification, 'alternativeLabel', [ i.name for i in programme.programmename_set.filter(name_is_primary=False) ])
                self._set_if(limitQualification, 'EQFLevel', self._translate_qf_level(programme.qf_ehea_level))
                vc_data['credentialSubject']['authorizationClaims']['limitQualification'].append(limitQualification)

        return vc_data

    def populate_vc_subject(self, report, institution, subject_tpl={}):
        """
        Return a credentialSubject object derived from subject_tpl
        """
        subject = deepcopy(subject_tpl)
        subject['id'] = self._translate_subject(institution)
        if 'authorizationClaims' not in subject:
            subject['authorizationClaims'] = {}
        subject['authorizationClaims']['id'] = self._translate_vc(report, institution)
        # official countries
        subject['authorizationClaims']['limitJurisdiction'] = []
        for location in institution.institutioncountry_set.filter(country_verified=True).iterator():
            subject['authorizationClaims']['limitJurisdiction'].append(self._translate_country(location.country))
        # QF levels for institutional reports
        if report.agency_esg_activity.activity_type.type in [ 'institutional', 'institutional/programme' ]:
            self._set_if(subject['authorizationClaims'], 'limitQFLevel', self._collect_qf_levels(institution))

        return subject

    def compose_vc(self, report):
        """
        Compose a VC by combining generic and per-institution parts
        """

        # Fill institution-independent data
        vc_offer = self.populate_vc(report)

        # Fill per-institution data
        subjects = []
        for institution in report.institutions.iterator():
            subjects.append(self.populate_vc_subject(report, institution, vc_offer['credentialSubject']))
        if len(subjects) > 1:
            vc_offer['credentialSubject'] = subjects
        else:
            vc_offer['credentialSubject'] = subjects[0]

        return vc_offer

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

    def _translate_vc(self, report, institution):
        return(self.vc_uri % ( report.id, institution.id ))

    def _translate_report(self, report):
        return(self.report_uri % report.id)

    def _translate_agency(self, agency):
        return(self.agency_uri % agency.id)

    def _translate_subject(self, institution):
        return(self.institution_uri % institution.id)

    def _translate_institution_identifier(self, identifier):
        return(self.institution_identifier_uri % identifier.id)

    def _translate_programme(self, programme):
        return(self.programme_uri % programme.id)

    def _translate_activity_type(self, activity_type):
        return activity_type.type

    def _translate_country(self, country):
        if country.generic_url:
            return country.generic_url
        else:
            return(self.country_uri % country.id)

    def _translate_qf_level(self, qf_ehea_level):
        return getattr(qf_ehea_level, 'level', None)

    def _translate_date(self, value):
        return value.strftime("%Y-%m-%dT%H:%M:%SZ") if hasattr(value, 'strftime') and callable(value.strftime) else None


@method_decorator(cache_control(max_age=settings.VC_CACHE_MAX_AGE), name='dispatch')
class DEQARVCIssue(VCIssue):
    """
    Generic DEQAR Verifiable Credential
    """
    permission_classes = []

    vc_template = json.loads("""
        {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://data.deqar.eu/context/v2.jsonld"
            ],
            "id": "***",
            "type": [
                "VerifiableCredential",
                "DeqarReport"
            ],
            "issuer": "***",
            "credentialSubject": [ ],
            "credentialSchema": {
                "id": "https://data.deqar.eu/schema/v1.json",
                "type": "JsonSchemaValidator2018"
            }
        }
    """)

    def populate_vc(self, report):
        vc_data = super().populate_vc(report)

        # additional report data
        vc_data['credentialSubject']['authorizationClaims']['accreditationStatus'] = report.status.status
        vc_data['credentialSubject']['authorizationClaims']['accreditationActivity'] = report.agency_esg_activity.activity

        # registered QA agency
        vc_data['issuer'] = {
            'id': self.eqar_did,
            'onBehalfOf': {
                'id': self._translate_agency(report.agency),
                'type': 'EqarRegisteredAgency',
                'acronym': report.agency.acronym_primary,
                'name': report.agency.name_primary,
                'registrationValidFrom': self._translate_date(report.agency.registration_start),
                'registrationExpirationDate': self._translate_date(report.agency.registration_valid_to)
            }
        }

        return vc_data

    def populate_vc_subject(self, report, institution, subject_tpl):
        subject = super().populate_vc_subject(report, institution, subject_tpl)
        subject['type'] = 'DeqarInstitution'
        subject['name'] = institution.name_primary
        self._set_if(subject, 'eterID', getattr(institution, 'eter_id', None) )
        subject['identifiers'] = []
        for identifier in institution.institutionidentifier_set.filter(agency__isnull=True):
            subject['identifiers'].append({
                'id': self._translate_institution_identifier(identifier),
                'identifier': identifier.identifier,
                'resource': identifier.resource
            })
        if not self._set_if(subject, 'legalName', getattr(institution.institutionname_set.filter(name_valid_to=None).first(), 'name_official', None) ):
            self._set_if(subject, 'legalName', getattr(institution.institutionname_set.order_by('name_valid_to').last(), 'name_official', None) )
        self._set_if(subject, 'location', [ f"{l.city}, {l.country.name_english}" if l.city else l.country.name_english for l in institution.institutioncountry_set.iterator() ] )
        self._set_if(subject, 'foundingDate', self._translate_date(institution.founding_date) )
        self._set_if(subject, 'dissolutionDate', self._translate_date(institution.closure_date) )

        return subject



@method_decorator(cache_control(max_age=settings.VC_CACHE_MAX_AGE), name='dispatch')
class EBSIVCIssue(VCIssue):
    """
    Specific view to issue EBSI-compliant Verifiable Accreditations (Diploma Use Case)
    """
    permission_classes = []

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

    def compose_vc(self, report):
        """
        Check status: only official reports can be issued as EBSI VC
        """
        if report.status_id != 1:
            raise NotFound(
                detail="Report is not marked as 'part of obligatory EQA system' and cannot be issued as EBSI VC."
            )
        return(super().compose_vc(report))

    def populate_vc(self, report):
        """
        Add additional data (quick fix)
        """
        vc_data = super().populate_vc(report)
        vc_data['issued'] = vc_data['issuanceDate']
        return(vc_data)

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
        if country.eu_controlled_vocab_atu:
            return country.eu_controlled_vocab_atu
        elif country.eu_controlled_vocab_country:
            return country.eu_controlled_vocab_country
        else:
            return super()._translate_country(country)

    def _translate_qf_level(self, qf_ehea_level):
        EQF_LEVELS = {
            'short cycle': 'http://data.europa.eu/snb/eqf/5',
            'first cycle': 'http://data.europa.eu/snb/eqf/6',
            'second cycle': 'http://data.europa.eu/snb/eqf/7',
            'third cycle': 'http://data.europa.eu/snb/eqf/8',
        }
        if qf_ehea_level:
            return EQF_LEVELS.get(qf_ehea_level.level, None)
        else:
            return None

