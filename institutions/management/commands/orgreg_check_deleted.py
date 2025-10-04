from django.core.management import BaseCommand
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

import requests
from urllib.parse import urljoin

from institutions.models import \
    Institution, \
    InstitutionName, \
    InstitutionCountry, \
    InstitutionHistoricalRelationship, \
    InstitutionHierarchicalRelationship

class Command(BaseCommand):
    help = 'Find local OrgReg-based objects that have been deleted in OrgReg'

    Collections = {
        'entities': {
            'key': 'BAS.ENTITYID.v',
            'model': Institution,
            'expr': 'eter_id',
            'pattern': '%s',
            'msg': 'Entity {orgreg} was deleted, but still exists as {deqar.deqar_id} {deqar.name_primary}'
        },
        'characteristics': {
            'key': 'CHAR.CHARID.v',
            'model': InstitutionName,
            'expr': 'name_source_note__iregex',
            'pattern': r'^\s*OrgReg-[0-9]{4}-%s(\s|$)',
            'msg': 'Name {orgreg} was deleted, but still exists for {deqar.institution.name_primary}'
        },
        'locations': {
            'key': 'LOCAT.LOCATID.v',
            'model': InstitutionCountry,
            'expr': 'country_source_note__iregex',
            'pattern': r'^\s*OrgReg-[0-9]{4}-%s(\s|$)',
            'msg': 'Location {orgreg} was deleted, but still exists for {deqar.institution.name_primary}'
        },
        'linkages': {
            'key': 'LINK.ID.v',
            'model': InstitutionHierarchicalRelationship,
            'expr': 'relationship_note__iregex',
            'pattern': r'^\s*OrgReg-[0-9]{4}-%s(\s|$)',
            'msg': 'Link {orgreg} was deleted, but still exists for {deqar.institution_child.name_primary} -> {deqar.institution_parent.name_primary}'
        },
        'demographics': {
            'key': 'DEMO.EVENTID.v',
            'model': InstitutionHistoricalRelationship,
            'expr': 'relationship_note__iregex',
            'pattern': r'^\s*OrgReg-[0-9]{4}-%s(\s|$)',
            'msg': 'Demographic event {orgreg} was deleted, but still exists for {deqar.institution_source.name_primary} <-> {deqar.institution_target.name_primary}'
        }
    }

    def _lookup_deqar_object(self, item):
        if item.get('collection') not in self.Collections:
            self.stdout.write(self.style.WARNING(f'No corresponding DEQAR model for collection: "{item.get("collection")}"'))
        else:
            qs = self.Collections[item['collection']]['model'].objects
            orgreg_id = item.get(self.Collections[item['collection']]['key'])
            for obj in qs.filter(**{ self.Collections[item['collection']]['expr']: self.Collections[item['collection']]['pattern'] % orgreg_id }):
                self.stdout.write(self.Collections[item['collection']]['msg'].format(orgreg=orgreg_id, deqar=obj))


    def handle(self, *args, **options):
        api_base = getattr(settings, "ORGREG_API_BASE", "https://register.orgreg.joanneum.at/api/2.0/")
        headers = {
            'X-API-Key': getattr(settings, "ORGREG_API_KEY", None)
        }
        request_timeout = getattr(settings, "ORGREG_REQUEST_TIMEOUT", 60)
        api_path = "data-mgmt/fetch-deleted"

        response = requests.get(
            urljoin(api_base, api_path),
            headers=headers,
            timeout=request_timeout
        )
        response.raise_for_status()

        for item in response.json():
            if item.get('deleted', False):
                self._lookup_deqar_object(item)

