import requests
from django.conf import settings

from institutions.models import Institution, InstitutionIdentifier, InstitutionQFEHEALevel, InstitutionCountry, \
    InstitutionName, InstitutionHistoricalRelationship, InstitutionHistoricalRelationshipType, \
    InstitutionHierarchicalRelationship, InstitutionHierarchicalRelationshipType
from institutions.orgreg.orgreg_reporter import OrgRegReporter


class OrgRegSynchronizer:
    def __init__(self, only_new=False, dry_run=True):
        self.api = "https://register.orgreg.joanneum.at/api/2.0/"
        self.api_key = getattr(settings, "ORGREG_API_KEY", '')
        self.only_new = only_new
        self.dry_run = dry_run
        self.orgreg_ids = []
        self.orgreg_record = {}
        self.inst = {}
        self.report = OrgRegReporter()
        self.colours = {
            'WARNING': '\033[93m',
            'ERROR': '\033[91m',
            'END': '\033[0m'
        }

    def collect_orgreg_ids_by_country(self, country_code):
        query_data = {
            "requestBy": {
                "requestedBy": "DEQAR"
            },
            "query": {
                "countries": [country_code] if country_code else [],
                "entityTypes": [1]
            },
            "fieldIDs": [
                "BAS.ENTITYID"
            ],
            "collections": [
                "entities"
            ]
        }
        headers = {'X-API-Key': self.api_key}

        r = requests.post(
            "%s%s" % (self.api, 'organizations/query'),
            json=query_data,
            headers=headers
        )

        if r.status_code == 201:
            response = r.json()
            self.orgreg_ids = list(map(lambda x: x['BAS']['ENTITYID']['v'], response['entities']))
            return True
        else:
            return False

    def collect_orgreg_ids_by_institution(self, orgreg_id):
        r = requests.get("%s%s%s" % (self.api, 'entity-details/', orgreg_id))
        if r.status_code == 200:
            self.orgreg_ids.append(orgreg_id)
            return True
        else:
            return False

    def get_orgreg_record(self, orgreg_id):
        r = requests.get("%s%s%s" % (self.api, 'entity-details/', orgreg_id))
        if r.status_code == 200:
            self.orgreg_record = r.json()
            return True
        else:
            return False

    def run(self):
        self.report.add_header()
        for index, orgreg_id in enumerate(self.orgreg_ids):
            print('\rProcessing institution %s (%d of %d)' % (orgreg_id, index+1, len(self.orgreg_ids)), end='', flush=True)
            institution = Institution.objects.filter(eter__eter_id=orgreg_id)
            if institution.count() > 0:
                self.inst = institution.first()
                self.report.add_institution_header(
                    orgreg_id=orgreg_id,
                    deqar_id=self.inst.deqar_id,
                    institution_name=self.inst.name_primary
                )
                self.get_orgreg_record(orgreg_id)
                self.sync_base_data()
                # self.sync_qf_ehea_levels(orgreg_id)
                self.sync_locations()
                self.sync_names()
                self.sync_historical_relationships()
                self.sync_hierarchical_relationships()
                self.report.add_empty_line()
        print('\n')
        print(self.report.get_report())

    def sync_base_data(self):
        # DEQAR ID
        self._compare_simple_data('DEQAR ID', self.inst.deqar_id, 'DEQARID', color=self.colours['ERROR'])

        # Founding Date
        founding_date = self.inst.founding_date.year if self.inst.founding_date else ''
        self._compare_simple_data('Founding year', founding_date, 'FOUNDYEAR')

        # Closing Date
        closure_date = self.inst.closure_date.year if self.inst.closure_date else ''
        self._compare_simple_data('Closing year', closure_date, 'ENTITYCLOSUREYEAR')

        # Website
        self._compare_simple_data('Website', self.inst.website_link, 'WEBSITE')

        # National ID
        if self.inst.national_identifier:
            self._compare_simple_data('National Identifier', self.inst.national_identifier[5:], 'NATID')
        else:
            self._compare_simple_data('National Identifier', '', 'NATID')

        # Erasmus Code
        self._compare_identifiers('Erasmus', 'ERASMUSCODE1420')

        # WHED Code
        self._compare_identifiers('WHED', 'WHEDID')

    def sync_names(self):
        names = self.orgreg_record['CHAR']
        for name in names:
            name_record = name['CHAR']
            name_official = self._get_value(name_record, 'INSTNAME')
            name_english = self._get_value(name_record, 'INSTNAMEENGL')
            acronym = self._get_value(name_record, 'ACRONYM')
            date_to = self._get_value(name_record, 'CHARENDYEAR', default=None)

            institution_name = InstitutionName.objects.filter(
                name_english=name_english,
            )
            if institution_name.count() > 0:
                iname = institution_name.first()
                values_to_update = {
                    'update': False,
                    'name_english': iname.name_english,
                    'name_official': iname.name_official,
                    'acronym': iname.acronym,
                    'name_valid_to': iname.name_valid_to
                }

                if name_english:
                    if iname.name_english != name_english:
                        values_to_update['update'] = True
                        values_to_update['name_english'] = "%s <- %s" % (iname.name_english, name_english)

                if name_official:
                    if iname.name_official != name_official:
                        values_to_update['update'] = True
                        values_to_update['name_official'] = "%s <- %s" % (iname.name_official, name_official)

                if date_to and iname.name_valid_to:
                    if iname.name_valid_to.year != date_to:
                        values_to_update['update'] = True
                        date_to = "%s-12-31" % date_to
                        values_to_update['name_valid_to'] = "%s <- %s" % (iname.name_valid_to, date_to)

                if values_to_update['update']:
                    self.report.add_report_line(
                        '**UPDATE - Name: (Name English: %s, Name Official: %s, Acronym: %s, Valid To: %s)' %
                        (values_to_update['name_english'], values_to_update['name_official'], values_to_update['acronym'], values_to_update['name_valid_to'])
                    )
            else:
                self.report.add_report_line(
                    '**ADD - Name: (Name English: %s, Name Official: %s, Acronym: %s, Valid To: %s)' %
                    (name_english, name_official, acronym, "%s-12-31" % date_to if date_to else None)
                )

    def sync_locations(self):
        locations = self.orgreg_record['LOCAT']
        for location in locations:
            location_record = location['LOCAT']
            country_code = self._get_value(location_record, 'LOCATCOUNTRY') if self._get_value(location_record, 'LOCATCOUNTRY') != 'GB' else 'UK'
            city = self._get_value(location_record, 'CITY')
            legal_seat = self._get_value(location_record, 'LEGALSEAT') == 1

            date_from = self._get_value(location_record, 'STARTYEAR', default=None)
            date_to = self._get_value(location_record, 'ENDYEAR', default=None)

            institution_country = InstitutionCountry.objects.filter(
                country__iso_3166_alpha2=country_code,
                city=city
            )
            # Location info exists, we should check for the legal seat.
            if institution_country.count() > 0:
                ic = institution_country.first()
                values_to_update = {
                    'update': False,
                    'legal_seat': 'YES' if ic.country_verified  else 'NO',
                    'date_from': ic.country_valid_from,
                    'date_to': ic.country_valid_to,
                }

                if ic.country_verified != legal_seat:
                    values_to_update['update'] = True
                    values_to_update['legal_seat'] = 'NO <- YES' if legal_seat else 'YES <- NO'

                if date_from:
                    if ic.country_valid_from.year != date_from:
                        values_to_update['update'] = True
                        date_from = "%s-01-01" % date_from
                        values_to_update['date_from'] = "%s <- %s" % (ic.country_valid_from, date_from)

                if date_to:
                    if ic.country_valid_to.year != date_to:
                        values_to_update['update'] = True
                        date_to = "%s-12-31" % date_to
                        values_to_update['date_to'] = "%s <- %s" % (ic.country_valid_to, date_to)

                if values_to_update['update']:
                    self.report.add_report_line(
                        '**UPDATE - Location: (Country: %s, City: %s, Official: %s, Valid From: %s, Valid To: %s)' %
                        (country_code, city, values_to_update['legal_seat'], values_to_update['date_from'], values_to_update['date_to'])
                    )
            else:
                self.report.add_report_line(
                    '**ADD - Location: (Country: %s, City: %s, Official: %s, Valid From: %s, Valid To: %s)' %
                    (country_code, city, 'YES' if legal_seat else 'NO', date_from, date_to)
                )

    def sync_historical_relationships(self):
        map = {
            '5': 2,
            '6': 2,
            '7': 3,
            '8': 4
        }
        relationships = self.orgreg_record['DEMO']
        for relationship in relationships:
            rel = relationship['DEMO']
            parent_id = self._get_value(rel, 'PARENTID')
            child_id = self._get_value(rel, 'CHILDID')
            event_type = str(self._get_value(rel, 'EVENTTYPE'))
            date = self._get_value(rel, 'EVENTYEAR', default=None)

            parent_institutions = Institution.objects.filter(eter__eter_id=parent_id)
            child_institutions = Institution.objects.filter(eter__eter_id=child_id)

            if parent_institutions.count() > 0 and child_institutions.count() > 0:
                parent_institution = parent_institutions.first()
                child_institution = child_institutions.first()

                if event_type in map.keys():
                    if event_type != '7':
                        deqar_relationships = InstitutionHistoricalRelationship.objects.filter(
                            institution_source=child_institution,
                            institution_target=parent_institution,
                            relationship_type__id=map[event_type]
                        )
                        if deqar_relationships.count() == 0:
                            deqar_event_type = InstitutionHistoricalRelationshipType.objects.get(pk=map[event_type])
                            self.report.add_report_line(
                                '**ADD - HISTORICAL RELATIONSHIP: (Source: %s, Target: %s, Relationship Type: %s, Date: %s)' %
                                (child_institution.eter, parent_institution.eter, deqar_event_type, "%s-01-01" % date)
                            )
                    else:
                        deqar_relationships = InstitutionHistoricalRelationship.objects.filter(
                            institution_source=parent_institution,
                            institution_target=child_institution,
                            relationship_type__id=map[event_type]
                        )
                        if deqar_relationships.count() == 0:
                            deqar_event_type = InstitutionHistoricalRelationshipType.objects.get(pk=map[event_type])
                            self.report.add_report_line(
                                '**ADD - HISTORICAL RELATIONSHIP: (Source: %s, Target: %s, Relationship Type: %s, Date: %s)' %
                                (parent_institution.eter, child_institution.eter, deqar_event_type, "%s-01-01" % date)
                            )


    def sync_hierarchical_relationships(self):
        map = {
            '1': 1,
            '2': 1,
        }
        relationships = self.orgreg_record['LINK']
        for relationship in relationships:
            rel = relationship['LINK']
            entity1 = self._get_value(rel, 'ENTITY1ID')
            entity2 = self._get_value(rel, 'ENTITY2ID')
            event_type = str(self._get_value(rel, 'TYPE'))
            date_from = self._get_value(rel, 'STARTYEAR', default=None)
            date_to = self._get_value(rel, 'ENDYEAR', default=None)


            parent_institutions = Institution.objects.filter(eter__eter_id=entity2)
            child_institutions = Institution.objects.filter(eter__eter_id=entity1)

            if parent_institutions.count() > 0 and child_institutions.count() > 0:
                parent_institution = parent_institutions.first()
                child_institution = child_institutions.first()

                if event_type in map.keys():
                    deqar_relationships = InstitutionHierarchicalRelationship.objects.filter(
                        institution_parent=parent_institution,
                        institution_child=child_institution,
                        relationship_type__id=map[event_type]
                    )
                    if deqar_relationships.count() == 0:
                        deqar_event_type = InstitutionHierarchicalRelationshipType.objects.get(pk=map[event_type])
                        self.report.add_report_line(
                            '**ADD - HIERARCHICAL RELATIONSHIP: (Parent: %s, Child: %s, Relationship Type: %s, Date (from): %s, Date (to): %s)' %
                            (parent_institution.eter,
                             child_institution.eter,
                             deqar_event_type,
                             "%s-01-01" % date_from if date_from else None,
                             "%s-12-31" % date_to if date_to else None)
                        )

    def sync_qf_ehea_levels(self, orgreg_id):
        query_data = {
          "filter": {
            "BAS.ETERID.v": orgreg_id,
            "BAS.REFYEAR.v": 2019
          },
          "fieldIds": [
            "BAS.REFYEAR",
            "STUD.LOWDEG",
            "STUD.HIGHDEG"
          ],
          "searchTerms": []
        }
        r = requests.post(
            'https://www.eter-project.com/api/3.0/HEIs/query',
            json=query_data,
        )
        if r.status_code == 200:
            response = r.json()
            low_level = response[0]['STUD']['LOWDEG']['v']
            high_level = response[0]['STUD']['HIGHDEG']['v']
        # TODO

    def _get_value(self, values_dict, key, default=''):
        return values_dict[key]['v'] if 'v' in values_dict[key].keys() else default

    def _compare_simple_data(self, label, deqar_value, orgreg_value, fallback_value=None, color=''):
        orgreg_val = None
        base_data = self.orgreg_record['BAS'][0]['BAS']

        if 'v' in base_data[orgreg_value].keys():
            orgreg_val = base_data[orgreg_value]['v']
        elif fallback_value:
                orgreg_val = base_data[fallback_value]['v']

        if orgreg_val:
            if deqar_value != orgreg_val:
                if deqar_value:
                    self.report.add_report_line(
                        '%s**UPDATE - %s: %s <-- %s%s' % (color, label, deqar_value, orgreg_val, self.colours['END']))
                else:
                    self.report.add_report_line(
                        '%s**ADD - %s: %s%s' % (color, label, orgreg_val, self.colours['END']))

    def _compare_identifiers(self, id_type, orgreg_id_value):
        inst_id = InstitutionIdentifier.objects.filter(institution=self.inst, resource=id_type)
        if inst_id.count() > 0:
            self._compare_simple_data(id_type, inst_id.identifier, orgreg_id_value)
        else:
            self._compare_simple_data(id_type, '', orgreg_id_value)
