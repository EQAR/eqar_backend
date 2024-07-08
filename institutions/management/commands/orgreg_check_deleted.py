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

    Translations = {
        'BAS.ENTITYID.v': {
            'model': Institution,
            'expr': 'eter_id',
            'pattern': '%s',
            'msg': 'Entity {orgreg} was deleted, but still exists as {deqar.deqar_id} {deqar.name_primary}'
        },
        'CHAR.CHARID.v': {
            'model': InstitutionName,
            'expr': 'name_source_note__iregex',
            'pattern': r'^\s*OrgReg-[0-9]{4}-%s(\s|$)',
            'msg': 'Name {orgreg} was deleted, but still exists for {deqar.institution.name_primary}'
        },
        'LOCAT.LOCATID.v': {
            'model': InstitutionCountry,
            'expr': 'country_source_note__iregex',
            'pattern': r'^\s*OrgReg-[0-9]{4}-%s(\s|$)',
            'msg': 'Location {orgreg} was deleted, but still exists for {deqar.institution.name_primary}'
        },
        'LINK.ID.v': {
            'model': InstitutionHierarchicalRelationship,
            'expr': 'relationship_note__iregex',
            'pattern': r'^\s*OrgReg-[0-9]{4}-%s(\s|$)',
            'msg': 'Link {orgreg} was deleted, but still exists for {deqar.institution_child.name_primary} -> {deqar.institution_parent.name_primary}'
        },
        'DEMO.EVENTID.v': {
            'model': InstitutionHistoricalRelationship,
            'expr': 'relationship_note__iregex',
            'pattern': r'^\s*OrgReg-[0-9]{4}-%s(\s|$)',
            'msg': 'Demographic event {orgreg} was deleted, but still exists for {deqar.institution_source.name_primary} <-> {deqar.institution_target.name_primary}'
        }
    }

    def _lookup_deqar_object(self, item):
        if item.get('keyFieldId') not in self.Translations:
            self.stdout.write(self.style.WARNING('No corresponding DEQAR model for keyFieldId: "{item.get("keyFieldId")}"'))
        else:
            qs = self.Translations[item['keyFieldId']]['model'].objects
            for obj in qs.filter(**{ self.Translations[item['keyFieldId']]['expr']: self.Translations[item['keyFieldId']]['pattern'] % item.get('keyFieldIdValue') }):
                self.stdout.write(self.Translations[item['keyFieldId']]['msg'].format(orgreg=item.get('keyFieldIdValue'), deqar=obj))


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

