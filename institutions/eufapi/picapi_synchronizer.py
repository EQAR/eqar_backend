import functools
import requests
import unicodedata
import re

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from institutions.models import Institution, InstitutionIdentifier
from lists.models import IdentifierResource

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class PicApiError(Exception):
    """
    Exception: error in communication with EU API
    """

class PicCodeNotFound(Exception):
    """
    Exception: PIC code recorded in DEQAR could not be found
    """

class PicApiSynchronizer:
    """
    Synchronises VAT IDs using the EU PIC API
    """

    # VAT and PIC identifier resources
    R_VAT = 'EU-VAT'
    R_PIC = 'EU-PIC'

    def __init__(self):
        self.api = getattr(settings, "EUPIC_API", "https://ec.europa.eu/info/funding-tenders/opportunities/api/organisation/search.json")
        # session for EU PIC API
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': 'DEQAR ' + self.session.headers['User-Agent'],
            'accept': 'application/json',
        })
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.request = functools.partial(self.session.request, timeout=getattr(settings, "EUPIC_API_TIMEOUT", 5), allow_redirects=True)

    def sync(self, institution, dry_run=True, pic=None):
        """
        Sync VAT ID for one institution
        """
        if not pic:
            try:
                iid = institution.institutionidentifier_set.get(resource=self.R_PIC)
                pic = iid.identifier
            except InstitutionIdentifier.DoesNotExist:
                return None

        query = self.session.post(self.api, json={ 'pic': pic })

        if query.status_code == requests.codes.ok:
            found = query.json()
            if len(found) == 1:
                vat = found[0]['vat']
                if vat is None or vat == '.' or vat == 'not applicable':
                    try:
                        iid = institution.institutionidentifier_set.get(resource=self.R_VAT)
                    except InstitutionIdentifier.DoesNotExist:
                        return (None, None)
                    else:
                        stats = (iid.identifier, None)
                        if not dry_run:
                            iid.delete()
                        return stats
                else:
                    try:
                        iid = institution.institutionidentifier_set.get(resource=self.R_VAT)
                    except InstitutionIdentifier.DoesNotExist:
                        if not dry_run:
                            iid = institution.institutionidentifier_set.create(
                                resource_id=self.R_VAT,
                                identifier=vat
                            )
                        return (None, vat)
                    else:
                        stats = (iid.identifier, vat)
                        if iid.identifier != vat and not dry_run:
                            iid.identifier = vat
                            iid.save()
                        return stats
            elif len(found) == 0:
                raise PicCodeNotFound(f'PIC code [{pic}] not found')
            else:
                raise PicApiError(f'PIC code [{pic}] is not unqiue - odd!')
        else:
            raise PicApiError(f'HTTP error {query.status_code} for PIC code [{pic}]')

