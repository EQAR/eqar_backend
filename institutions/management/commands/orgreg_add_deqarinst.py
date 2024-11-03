from django.conf import settings
from django.core.management import BaseCommand

import argparse
import csv

import requests

from institutions.models import Institution


class Command(BaseCommand):
    help = 'Generate a list of DEQARINST IDs that should be added to OrgReg'

    def add_arguments(self, parser):
        parser.add_argument('FILE', help='Output list as CSV (use - for stdout)',
                            type=argparse.FileType('w'))

    def handle(self, *args, FILE, **options):
        self.api = "https://register.orgreg.joanneum.at/api/2.0/"
        self.orgreg_ids_blacklist = getattr(settings, "ORGREG_ID_BLACKLIST", [])
        self.orgreg_session = requests.Session()
        if hasattr(settings, "ORGREG_API_KEY"):
            self.orgreg_session.headers.update({'X-API-Key': getattr(settings, "ORGREG_API_KEY")})
        self.request_timeout = getattr(settings, "ORGREG_REQUEST_TIMEOUT", 60)

        query_data = {
            "requestBy": {
                "requestedBy": "DEQAR"
            },
            "query": {
                "entityTypes": [1]
            },
            "fieldIDs": [
                "BAS.ENTITYID",
                "BAS.DEQARID"
            ],
            "collections": [
                "entities"
            ]
        }

        r = self.orgreg_session.post(
            "%s%s" % (self.api, 'organizations/query'),
            json=query_data,
            timeout=self.request_timeout
        )
        r.raise_for_status()
        response = r.json()

        writer = csv.DictWriter(FILE, fieldnames=['BAS.ENTITYID', 'BAS.DEQARID'])

        for entity in response['entities']:
            orgreg_id = entity['BAS']['ENTITYID']['v']
            orgreg_deqar_id = entity['BAS']['DEQARID']['v'] if 'DEQARID' in entity['BAS'] and 'v' in entity['BAS']['DEQARID'] else None

            if orgreg_deqar_id:
                # check for inconsistencies
                try:
                    hei = Institution.objects.get(deqar_id=orgreg_deqar_id)
                    if hei.eter_id != orgreg_id:
                        self.stderr.write(self.style.ERROR(f"Entity {orgreg_id} has DEQAR ID {orgreg_deqar_id} listed in OrgReg, while that one has {hei.eter_id} listed as ETER ID in DEQAR"))
                except Institution.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f"Entity {orgreg_id} has an unknown DEQAR ID [{orgreg_deqar_id}] listed in OrgReg"))
                # reverse check: by OrgReg ID
                try:
                    hei = Institution.objects.get(eter_id=orgreg_id)
                    if hei.deqar_id != orgreg_deqar_id:
                        self.stderr.write(self.style.ERROR(f"Entity {orgreg_id} has DEQAR ID {orgreg_deqar_id} listed in OrgReg, while {hei.deqar_id} has that OrgReg ID in DEQAR"))
                except Institution.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f"Entity {orgreg_id} has DEQAR ID {orgreg_deqar_id} listed in OrgReg, but OrgReg ID is not recorded in DEQAR."))
                except Institution.MultipleObjectsReturned:
                    self.non_unique_id_error(orgreg_id)
            else:
                # no DEQARINST ID in OrgReg -> add to list, unless consistency issues occur
                try:
                    hei = Institution.objects.get(eter_id=orgreg_id)
                    if orgreg_id not in self.orgreg_ids_blacklist:
                        writer.writerow({
                            'BAS.ENTITYID': orgreg_id,
                            'BAS.DEQARID': hei.deqar_id,
                        })
                    else:
                        self.stderr.write(self.style.WARNING(f"Entity {orgreg_id} is blacklisted in DEQAR, ignoring."))
                except Institution.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f"OrgReg ID {orgreg_id} is not (yet) known in DEQAR"))
                except Institution.MultipleObjectsReturned:
                    self.non_unique_id_error(orgreg_id)

    def non_unique_id_error(self, orgreg_id):
        heis = ", ".join(Institution.objects.filter(eter_id=orgreg_id).values_list('deqar_id', flat=True))
        self.stderr.write(self.style.ERROR(f"Multiple DEQAR Institution records are linked to OrgReg ID {orgreg_id}: {heis}"))

