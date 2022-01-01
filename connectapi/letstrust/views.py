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
    View to issue generic W3C-compliant Verifiable Credentials (VC)
    """

    # Provisional workaround: hard-coded template
    vc_template = json.loads("""
        {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://data.deqar.eu/context/v1.jsonld"
            ],
            "id": "***",
            "type": [
                "VerifiableCredential"
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

    def collect_vcs(self, report):
        """
        Use the template and create one VC per institution covered
        """
        post_data_log = []

        # Fill the json with report data
        template = deepcopy(self.vc_template)
        template['id'] = 'https://data.deqar.eu/report/%s' % report.id
        template['issuer'] = self.eqar_did
        template['issuanceDate'] = report.valid_from.strftime("%Y-%m-%dT%H:%M:%SZ")
        template['validFrom'] = report.valid_from.strftime("%Y-%m-%dT%H:%M:%SZ")
        if report.valid_to:
            template['expirationDate'] = report.valid_to.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            template['expirationDate'] = (report.valid_from + datedelta(years=6)).strftime("%Y-%m-%dT%H:%M:%SZ")
        template['credentialSubject']['authorizationClaims']['accreditationType'] = self._translate_activity_type(report.agency_esg_activity.activity_type)
        template['credentialSubject']['authorizationClaims']['accreditationStatus'] = report.status.status
        template['credentialSubject']['authorizationClaims']['decision'] = report.decision.decision

        # Report files
        for reportfile in report.reportfile_set.iterator():
            try:
                template['credentialSubject']['authorizationClaims']['report'].append(self.request.build_absolute_uri(reportfile.file.url))
            except (ValueError):
                pass

        # Programme data
        if report.agency_esg_activity.activity_type.type in [ 'programme', 'joint programme' ]:
            template['credentialSubject']['authorizationClaims']['limitQualification'] = []
            for programme in report.programme_set.iterator():
                limitQualification = {}
                limitQualification['title'] = programme.programmename_set.filter(name_is_primary=True).first().name
                limitQualification['alternativeLabel'] = [ i.name for i in programme.programmename_set.filter(name_is_primary=False) ]
                if programme.qf_ehea_level:
                    limitQualification['EQFLevel'] = self._translate_qf_level(programme.qf_ehea_level)
                template['credentialSubject']['authorizationClaims']['limitQualification'].append(limitQualification)

        # Iterate over institutions
        for institution in report.institutions.iterator():
            vc_offer = deepcopy(template)
            vc_offer['credentialSubject']['id'] = self._translate_subject(institution)

            # official countries
            for location in institution.institutioncountry_set.filter(country_verified=True).iterator():
                vc_offer['credentialSubject']['authorizationClaims']['limitJurisdiction'].append(self._translate_country(location.country))

            # QF levels
            if report.agency_esg_activity.activity_type.type not in [ 'programme', 'joint programme' ]:
                qf_levels = self._collect_qf_levels(institution)
                if qf_levels:
                    vc_offer['credentialSubject']['authorizationClaims']['limitQFLevel'] = qf_levels

            result = self.issue_vc(None, vc_offer)
            result["institution"] = { 'id': institution.id, 'deqar_id': institution.deqar_id, 'name_primary': institution.name_primary }
            post_data_log.append(result)

        return Response(post_data_log)

    def _collect_qf_levels(self, institution):
        qf_levels = set()
        for level in institution.institutionqfehealevel_set.iterator():
            if self._translate_qf_level(level.qf_ehea_level):
                qf_levels.add(self._translate_qf_level(level.qf_ehea_level))
        return list(qf_levels)

    """
    Helper functions, meant to be overwritten in subclasses (e.g. EBSI-specific)
    """

    def _translate_subject(self, institution):
        return('https://data.deqar.eu/institution/%s' % institution.id)

    def _translate_activity_type(self, activity_type):
        return activity_type.type

    def _translate_country(self, country):
        return country.iso_3166_alpha3.upper()

    def _translate_qf_level(self, qf_ehea_level):
        return qf_ehea_level.level


class EBSIVCIssue(VCIssue):
    """
    Specific view to issue EBSI-compliant Verifiable Accreditations (Diploma Use Case)
    """

    # EBSI-specific template
    vc_template = json.loads("""
        {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://data.deqar.eu/context/v1.jsonld"
            ],
            "id": "***",
            "type": [
                "VerifiableCredential",
                "VerifiableAttestation"
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
                "id": "https://ec.europa.eu/cefdigital/code/projects/EBSI/repos/json-schema/raw/ebsi-muti-uni-pilot/Education%20Verifiable%20Accreditation%20Records-generated-schema.json",
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

    def issue_vc(self, subject_did, offer):
        """
        Mask accreditationStatus from EBSI VCs
        """
        offer['credentialSubject']['authorizationClaims'].pop('accreditationStatus', None)
        return(super().issue_vc(subject_did, offer))

    def collect_vcs(self, report):
        """
        Check status: only official reports can be issued as EBSI VC
        """
        if report.status_id != 1:
            raise NotFound(
                detail="Report is not marked as 'part of obligatory EQA system' and cannot be issued as EBSI VC."
            )
        return(super().collect_vcs(report))

    def _translate_subject(self, institution):
        """
        Get EBSI DID of the institutions mentioned in the report
        """
        institution_did = InstitutionIdentifier.objects.filter(Q(institution=institution) | Q(institution__relationship_parent__institution_child=institution), resource='DID-EBSI').first()
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

