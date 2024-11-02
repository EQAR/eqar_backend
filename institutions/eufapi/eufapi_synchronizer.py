import functools
import requests
import unicodedata
import re

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from institutions.models import Institution, InstitutionIdentifier
from lists.models import IdentifierResource

class EufApiError(Exception):
    """
    Exception: error when talking to EUF API
    """

class ErasmusCodeSyntaxError(Exception):
    """
    Exception: Erasmus code from DEQAR could not be normalized
    """

class ErasmusCodeNotFound(Exception):
    """
    Exception: Erasmus code recorded in DEQAR was not found in EUF API
    """

class HeiApiSynchronizer:
    """
    Synchronises identifiers from the EUF HEI API
    """

    # Mapping of HEI API types to DEQAR identifier resources
    IDMAP = {
        None: 'SCHAC',
        'erasmus-charter': 'Erasmus-Charter',
        'erasmus': 'Erasmus',
        'pic': 'EU-PIC'
    }

    # Erasmus and SCHAC identifier resources
    R_ERASMUS = 'Erasmus'
    R_SCHAC = 'SCHAC'

    def __init__(self):
        self.api = getattr(settings, "EUFHEI_API", "https://hei.api.uni-foundation.eu/api/public/v1/hei")
        # session for EUF HEI API
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': 'DEQAR ' + self.session.headers['User-Agent'],
            'accept': 'application/json',
        })
        self.session.request = functools.partial(self.session.request, timeout=getattr(settings, "EUFHEI_API_TIMEOUT", 5), allow_redirects=True)

    def _normalize_erasmus(self, code):
        """
        Normalize Erasmus codes
        (follows the methodology described at https://eche-list.erasmuswithoutpaper.eu/docs/01_ECHE_DATA/02_ERASMUS.md)
        """
        code = unicodedata.normalize('NFKC', code)

        if re.match(r'^(IRL|LUX|[A-Z]{2}[ ]{1}|[A-Z]{1}[ ]{2})[A-Z][A-Z-]*[A-Z]\d{2,3}$', code):
            # already normalized
            return (code, True)
        elif match := re.match(r'^\s*(IRL|LUX|[A-Z]{1,2}\s)\s*(\D+)(\d{1,3})\s*$', code, re.IGNORECASE):
            # can be normalized
            country = match[1].strip().upper()
            city = re.sub(r'[^A-Z]', '-', match[2].upper())
            num = int(match[3])
            return (f'{country:3}{city}{num:02d}', False)
        else:
            raise ErasmusCodeSyntaxError(f'Erasmus code [{code}] could not be normalized.')


    def load(self):
        """
        Loads the full list of HEIs from the EUF API
        """
        try:
            result = self.session.get(self.api)
            hei_list = result.json()['data']
        except KeyError:
            raise EufApiError('Received unexpectedly formed JSON from EUF API.')

        stats = {
            'received': len(hei_list),
            'has_erasmus': 0,
            'has_schac': 0,
            'duplicate_erasmus': set(),
            'duplicate_schac': set(),
        }
        self.heis_by_erasmus = dict()
        self.heis_by_schac = dict()

        for hei in hei_list:
            record = { self.IDMAP[None]: hei['id'] }
            if isinstance(hei['attributes']['other_id'], list):
                ids = hei['attributes']['other_id']
            elif isinstance(hei['attributes']['other_id'], dict):
                ids = [ hei['attributes']['other_id'] ]
            else:
                ids = [ ]
            for i in ids:
                if i['type'] in self.IDMAP:
                    record[self.IDMAP[i['type']]] = i['value']
            # save under Erasmus code
            if self.R_ERASMUS in record and record[self.R_ERASMUS] not in stats['duplicate_erasmus']:
                if record[self.R_ERASMUS] in self.heis_by_erasmus and record != self.heis_by_erasmus[record[self.R_ERASMUS]]:
                    stats['duplicate_erasmus'].add(record[self.R_ERASMUS])
                    del self.heis_by_erasmus[record[self.R_ERASMUS]]
                else:
                    self.heis_by_erasmus[record[self.R_ERASMUS]] = record
                    stats['has_erasmus'] += 1
            # save under SCHAC code
            if self.R_SCHAC in record and record[self.R_SCHAC] not in stats['duplicate_schac']:
                if record[self.R_SCHAC] in self.heis_by_schac and record != self.heis_by_schac[record[self.R_SCHAC]]:
                    stats['duplicate_schac'].add(record[self.R_SCHAC])
                    del self.heis_by_schac[record[self.R_SCHAC]]
                else:
                    self.heis_by_schac[record[self.R_SCHAC]] = record
                    stats['has_schac'] += 1

        return stats

    def sync(self, institution, dry_run=True):
        """
        Sync identifiers for one institution
        """
        try:
            erasmus = institution.institutionidentifier_set.get(resource=self.R_ERASMUS)
        except InstitutionIdentifier.DoesNotExist:
            return None
        else:
            stats = {}
            (lookup, was_normalized) = self._normalize_erasmus(erasmus.identifier)
            if not was_normalized:
                stats[self.R_ERASMUS] = (erasmus.identifier, lookup)
            if lookup in self.heis_by_erasmus:
                for (resource, identifier) in self.heis_by_erasmus[lookup].items():
                    try:
                        iid = institution.institutionidentifier_set.get(resource=resource)
                    except InstitutionIdentifier.DoesNotExist:
                        stats[resource] = (None, identifier)
                        if not dry_run:
                            iid = institution.institutionidentifier_set.create(
                                resource_id=resource,
                                identifier=identifier,
                            )
                    else:
                        stats[resource] = (iid.identifier, identifier)
                        if iid.identifier != identifier and not dry_run:
                            iid.identifier = identifier
                            iid.save()
                return stats
            else:
                raise ErasmusCodeNotFound(f'Erasmus code [{lookup}] recorded in DEQAR not found in HEI API')

