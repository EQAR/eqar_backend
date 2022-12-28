from datetime import datetime

import requests
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from countries.models import Country
from institutions.models import Institution, InstitutionIdentifier, InstitutionCountry, \
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
        self.inst_update = False
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
            # print('\rProcessing institution %s (%d of %d)' % (orgreg_id, index+1, len(self.orgreg_ids)), end='', flush=True)

            try:
                self.inst = Institution.objects.get(eter__eter_id=orgreg_id)
                action = 'update'
            except ObjectDoesNotExist:
                self.report.add_report_line(
                    "Institution with OrgReg ID [%s] doesn't exists. The record will be created!" % orgreg_id
                )
                action = 'add'
            except MultipleObjectsReturned:
                self.report.add_report_line("Multiple institutions with OrgReg ID [%s] exist." % orgreg_id)
                break

            self.get_orgreg_record(orgreg_id)

            if action == 'add':
                self.create_institution_record()
                self.inst.create_deqar_id()

                base_data = self.orgreg_record['BAS'][0]['BAS']
                self.report.add_institution_header(
                    orgreg_id=orgreg_id,
                    deqar_id=self.inst.deqar_id,
                    institution_name=self._get_value(base_data, 'ENTITYNAME', default="-NEW INSTITUTION-"),
                    action='CREATE'
                )

            if action == 'update':
                self.report.add_institution_header(
                    orgreg_id=orgreg_id,
                    deqar_id=self.inst.deqar_id,
                    institution_name=self.inst.name_primary
                )

            self.sync_base_data()
            self.sync_locations()
            self.sync_names()
            self.sync_historical_relationships()
            self.sync_hierarchical_relationships()
            self.report.add_empty_line()

            print(self.report.get_report())
            self.report.reset_report()

    def create_institution_record(self):
        compare = self._compare_base_data('Website', self.inst.website_link, 'WEBSITE')

        if compare['action'] != 'None':
            self.inst = Institution.objects.create(
                website_link=compare['orgreg_value']
            )
        else:
            self.inst = Institution.objects.create(
                website_link="N/A"
            )

    def sync_base_data(self):
        # DEQAR ID
        compare = self._compare_base_data('DEQAR ID', self.inst.deqar_id, 'DEQARID', color=self.colours['ERROR'])

        # Only continue if DEQAR ID is the same in both systems.
        if compare['action'] == 'None':
            # Founding Date
            founding_date = self.inst.founding_date.year if self.inst.founding_date else ''
            compare = self._compare_base_data('Founding year', founding_date, 'FOUNDYEAR', is_date=True)
            self._update_base_data('founding_date', compare)

            # Closing Date
            closure_date = self.inst.closure_date.year if self.inst.closure_date else ''
            compare = self._compare_base_data('Closing year', closure_date, 'ENTITYCLOSUREYEAR', is_date=True)
            self._update_base_data('closure_date', compare)

            # Website
            compare = self._compare_base_data('Website', self.inst.website_link, 'WEBSITE')
            self._update_base_data('website_link', compare)

            # Erasmus Code
            self._compare_identifiers('Erasmus', 'ERASMUSCODE1420')

            # WHED Code
            self._compare_identifiers('WHED', 'WHEDID')

            if self.inst_update:
                self.inst.save()

    def sync_national_identifier(self):
        base_record = self.orgreg_record['BAS'][0]
        nat_id = self._get_value(base_record, 'NATID', default=None)
        country = self._get_value(base_record, 'COUNTRY', default=None)
        action = 'skip'

        if nat_id and country:
            try:
                iid = InstitutionIdentifier.objects.get(
                    institution=self.inst,
                    resource="%s-ETER.BAS.NATID" % country
                )
                if iid.identifier != nat_id:
                    action = 'update'
            except MultipleObjectsReturned:
                self.report.add_report_line("%s**ERROR - More than one InstitutionIdentifier record exists with the "
                                            "same resource [%s]. Skipping.%s"
                                            % (self.colours['ERROR'],
                                               "%s-ETER.BAS.NATID" % country,
                                               self.colours['END']))
            except ObjectDoesNotExist:
                action = 'add'

        if action == 'update':
            self.report.add_report_line('**UPDATE - IDENTIFIER RECORD')
            self.report.add_report_line('  Identifier: %s <- %s ' % (iid.identifier, nat_id))
            self.report.add_report_line('  Resource: %s' % ("%s-ETER.BAS.NATID" % country))

            # Update InstiutionIdentifier
            if not self.dry_run:
                iid.identifier = nat_id
                iid.save()

        elif action == 'add':
            self.report.add_report_line('**ADD - IDENTIFIER RECORD')
            self.report.add_report_line('  Identifier: %s' % nat_id)
            self.report.add_report_line('  Resource: %s' % ("%s-ETER.BAS.NATID" % country))

            # Create InstiutionIdentifier
            if not self.dry_run:
                InstitutionIdentifier.objects.create(
                    institution=self.inst,
                    resource="%s-ETER.BAS.NATID" % country,
                    identifier=nat_id
                )

    def sync_names(self):
        names = self.orgreg_record['CHAR']
        for name in names:
            name_record = name['CHAR']
            name_orgreg_id = self._get_value(name_record, 'CHARID')
            name_official = self._get_value(name_record, 'INSTNAME')
            name_english = self._get_value(name_record, 'INSTNAMEENGL')

            if name_english == name_official:
                name_english = ''

            acronym = self._get_value(name_record, 'ACRONYM')
            date_to = self._get_date_value(name_record, 'CHARENDYEAR', default=None)

            action = 'skip'

            source_note = 'OrgReg-%s-%s %s' % (
                datetime.now().year,
                name_orgreg_id,
                self._get_value(name_record, 'NOTESCHARSTARTYEAR')
            )

            try:
                iname = InstitutionName.objects.get(
                    name_source_note__iregex=r'^\s*OrgReg-[0-9]{4}-%s' % name_orgreg_id
                )
                action = 'update'
            except MultipleObjectsReturned:
                self.report.add_report_line("%s**ERROR - More than one InstitutionName record exists with the "
                                            "same OrgReg ID [%s]. Skipping.%s"
                                            % (self.colours['ERROR'],
                                               name_orgreg_id,
                                               self.colours['END']))
            except ObjectDoesNotExist:
                try:
                    iname = InstitutionName.objects.get(
                        institution=self.inst,
                        name_official=name_official,
                        name_english=name_english
                    )
                    action = 'update'
                except MultipleObjectsReturned:
                    self.report.add_report_line("%s**ERROR - More than one InstitutionName record exists with the "
                                                "same English (%s) and Official Name (%s). Skipping.%s"
                                                % (self.colours['ERROR'],
                                                   name_english,
                                                   name_official,
                                                   self.colours['END']))
                except ObjectDoesNotExist:
                    action = 'add'

            # UPDATE NAME RECORD
            if action == 'update':
                values_to_update = {
                    'name_english': self._compare_data(iname.name_english, name_english),
                    'name_official': self._compare_data(iname.name_official, name_official),
                    'acronym': self._compare_data(iname.acronym, acronym),
                    'name_valid_to': self._compare_date_data(iname.name_valid_to, date_to, '%s-12-31')
                }

                if self._check_update(values_to_update):
                    self.report.add_report_line('**UPDATE - NAME RECORD')
                    self.report.add_report_line('  Name English: %s' % values_to_update['name_english']['log'])
                    self.report.add_report_line('  Name Official: %s' % values_to_update['name_official']['log'])
                    self.report.add_report_line('  Acronym: %s' % values_to_update['acronym']['log'])
                    self.report.add_report_line('  Valid To: %s' % values_to_update['name_valid_to']['log'])
                    self.report.add_report_line('  Source Note: %s' % source_note)

                    # Update InstiutionName record
                    if not self.dry_run:
                        iname.name_english = values_to_update['name_english']['value']
                        iname.name_official = values_to_update['name_official']['value']
                        iname.acronym = values_to_update['acronym']['value']
                        iname.name_valid_to = values_to_update['name_valid_to']['value']
                        iname.name_source_note = source_note
                        iname.save()

            # ADD NAME RECORD
            elif action == 'add':
                self.report.add_report_line('**ADD - NAME RECORD')
                self.report.add_report_line('  Name English: %s' % name_english)
                self.report.add_report_line('  Name Official: %s' % name_official)
                self.report.add_report_line('  Acronym: %s' % acronym)
                self.report.add_report_line('  Valid To: %s' % ("%s-12-31" % date_to['value'] if date_to['value'] else None))
                self.report.add_report_line('  Source Note: %s' % source_note)

                # Create InstiutionName record
                if not self.dry_run:
                    InstitutionName.objects.create(
                        institution=self.inst,
                        name_english=name_english,
                        name_official=name_official,
                        acronym=acronym,
                        name_valid_to="%s-12-31" % date_to['value'] if date_to['value'] else None,
                        name_source_note=source_note
                    )

    def sync_locations(self):
        locations = self.orgreg_record['LOCAT']
        for location in locations:
            location_record = location['LOCAT']
            location_orgreg_id = self._get_value(location_record, 'LOCATID')
            country_code = self._get_value(location_record, 'LOCATCOUNTRY')

            try:
                country = Country.objects.get(orgreg_eu_2_letter_code=country_code)
            except ObjectDoesNotExist:
                return

            city = self._get_value(location_record, 'CITY')
            legal_seat = self._get_value(location_record, 'LEGALSEAT') == 1

            date_from = self._get_date_value(location_record, 'STARTYEAR', default=None)
            date_to = self._get_date_value(location_record, 'ENDYEAR', default=None)

            source_note = 'OrgReg-%s-%s %s' % (
                datetime.now().year, location_orgreg_id, self._get_value(location_record, 'NOTESREG')
            )

            action = 'skip'

            try:
                ic = InstitutionCountry.objects.get(
                    country_source_note__iregex=r'^\s*OrgReg-[0-9]{4}-%s' % location_orgreg_id
                )
                action = 'update'
            except MultipleObjectsReturned:
                self.report.add_report_line("%s**ERROR - More than one InstitutionCountry record exists with the "
                                            "same OrgReg ID [%s]. Skipping.%s"
                                            % (self.colours['ERROR'],
                                               location_orgreg_id,
                                               self.colours['END']))
            except ObjectDoesNotExist:
                try:
                    ic = InstitutionCountry.objects.get(
                        institution=self.inst,
                        country=country,
                        city=city
                    )
                    action = 'update'
                except MultipleObjectsReturned:
                    self.report.add_report_line("%s**ERROR - More than one InstitutionCountry record exists with the "
                                                "same country (%s) and city (%s). Skipping.%s"
                                                % (self.colours['ERROR'],
                                                   country_code,
                                                   city,
                                                   self.colours['END'],))
                except ObjectDoesNotExist:
                    action = 'add'

            # UPDATE COUNTRY RECORD
            if action == 'update':
                values_to_update = {
                    'legal_seat': self._compare_boolean_data(ic.country_verified, legal_seat),
                    'date_from': self._compare_date_data(ic.country_valid_from, date_from, '%s-01-01'),
                    'date_to': self._compare_date_data(ic.country_valid_to, date_to, '%s-12-31')
                }

                if self._check_update(values_to_update):
                    self.report.add_report_line('**UPDATE - LOCATION')
                    self.report.add_report_line('  Country: %s' % country_code)
                    self.report.add_report_line('  City: %s' % city)
                    self.report.add_report_line('  Official: %s' % values_to_update['legal_seat']['log'])
                    self.report.add_report_line('  Valid From: %s' % values_to_update['date_from']['log'])
                    self.report.add_report_line('  Valid To: %s' % values_to_update['date_to']['log'])
                    self.report.add_report_line('  Source Note: %s' % source_note.strip())

                    # Update InstitutionCountry record
                    if not self.dry_run:
                        ic.country = country
                        ic.city = city
                        ic.country_verified = values_to_update['legal_seat']['value']
                        ic.country_valid_from = values_to_update['date_from']['value']
                        ic.country_valid_to = values_to_update['date_to']['value']
                        ic.country_source_note = source_note.strip()
                        ic.save()

            # ADD COUNTRY RECORD
            elif action == 'add':
                self.report.add_report_line('**ADD - LOCATION')
                self.report.add_report_line('  Country: %s' % country_code)
                self.report.add_report_line('  City: %s' % city)
                self.report.add_report_line('  Official: %s' % ('YES' if legal_seat else 'NO'))
                self.report.add_report_line('  Valid From: %s' % ("%s-01-01" % date_from['value'] if date_from['value'] else None))
                self.report.add_report_line('  Valid To: %s' % ("%s-12-31" % date_to['value'] if date_to['value'] else None))
                self.report.add_report_line('  Source Note: %s' % source_note.strip())

                # Create InstitutionCountry record
                if not self.dry_run:
                    InstitutionCountry.objects.create(
                        institution=self.inst,
                        country=country,
                        city=city,
                        country_verified=legal_seat,
                        country_valid_from="%s-01-01" % date_from['value'] if date_from['value'] else None,
                        country_valid_to="%s-12-31" % date_to['value'] if date_to['value'] else None,
                        country_source_note=source_note.strip()
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
            event_orgreg_id = self._get_value(rel, 'EVENTID')
            event_type = str(self._get_value(rel, 'EVENTTYPE'))

            if event_type == '7':
                source_id = self._get_value(rel, 'CHILDID')
                target_id = self._get_value(rel, 'PARENTID')
            else:
                source_id = self._get_value(rel, 'PARENTID')
                target_id = self._get_value(rel, 'CHILDID')

            date = self._get_date_value(rel, 'EVENTYEAR', default=None)

            source_note = 'OrgReg-%s-%s %s' % (
                datetime.now().year, event_orgreg_id, self._get_value(rel, 'NOTES')
            )

            action = 'skip'

            try:
                source_institution = Institution.objects.get(eter__eter_id=source_id)
            except ObjectDoesNotExist:
                self.report.add_report_line("%s**WARNING - Source Institution doesn't exist with OrgReg ID [%s]. Skipping.%s"
                                            % (self.colours['WARNING'],
                                               source_id,
                                               self.colours['END']))
                return
            except MultipleObjectsReturned:
                self.report.add_report_line("%s**ERROR - Multiple Source Institution exist with OrgReg ID [%s]. Skipping.%s"
                                            % (self.colours['ERROR'],
                                               source_id,
                                               self.colours['END']))
                return

            try:
                target_institution = Institution.objects.get(eter__eter_id=target_id)
            except ObjectDoesNotExist:
                self.report.add_report_line("%s**WARNING - Target Institution doesn't exist with OrgReg ID [%s]. Skipping.%s"
                                            % (self.colours['WARNING'],
                                               target_id,
                                               self.colours['END']))
                return
            except MultipleObjectsReturned:
                self.report.add_report_line("%s**ERROR - Multiple Target Institution exist with OrgReg ID [%s]. Skipping.%s"
                                            % (self.colours['WARNING'],
                                               target_id,
                                               self.colours['END']))
                return

            try:
                ihr = InstitutionHistoricalRelationship.objects.get(
                    relationship_note__iregex=r'^\s*OrgReg-[0-9]{4}-%s' % event_orgreg_id
                )
                action = 'update'
            except MultipleObjectsReturned:
                self.report.add_report_line("%s**ERROR - More than one InstitutionHistoricalRelationship record exists with the "
                                            "same OrgReg ID [%s]. Skipping.%s"
                                            % (self.colours['ERROR'],
                                               event_orgreg_id,
                                               self.colours['END']))
            except ObjectDoesNotExist:
                action = 'add'

            if event_type in map.keys():
                deqar_event_type = InstitutionHistoricalRelationshipType.objects.get(pk=map[event_type])
            else:
                self.report.add_report_line("%s**ERROR - Matching EventType can't be found [%s]. Skipping.%s"
                                            % (self.colours['ERROR'],
                                               event_type,
                                               self.colours['END']))
                return

            # UPDATE RELATIONSHIP RECORD
            if action == 'update':
                values_to_update = {
                    'source': self._compare_data(ihr.institution_source, source_institution),
                    'target': self._compare_data(ihr.institution_target, target_institution),
                    'type': self._compare_data(ihr.relationship_type, deqar_event_type),
                    'date': self._compare_date_data(ihr.relationship_date, date, "%s-01-01")
                }

                if self._check_update(values_to_update):
                    self.report.add_report_line('**UPDATE - HISTORICAL RELATIONSHIP')
                    self.report.add_report_line('  Source: %s' % values_to_update['source']['log'])
                    self.report.add_report_line('  Target: %s' % values_to_update['target']['log'])
                    self.report.add_report_line('  Relationship Type: %s' % values_to_update['type']['log'])
                    self.report.add_report_line('  Date: %s' % values_to_update['date']['log'])
                    self.report.add_report_line('  Source Note: %s' % source_note)

                    # Update InstitutionHistoricalRelationship record
                    if not self.dry_run:
                        ihr.institution_source = source_institution
                        ihr.institution_target = target_institution
                        ihr.relationship_date = values_to_update['date']['value']
                        ihr.relationship_note = source_note
                        ihr.save()

            # ADD RELATIONSHIP RECORD
            elif action == 'add':
                self.report.add_report_line('**ADD - HISTORICAL RELATIONSHIP')
                self.report.add_report_line('  Source: %s' % source_institution.eter)
                self.report.add_report_line('  Target: %s' % target_institution.eter)
                self.report.add_report_line('  Relationship Type: %s' % deqar_event_type)
                self.report.add_report_line('  Date: %s' % ("%s-01-01" % date['value'] if date['value'] else None))
                self.report.add_report_line('  Source Note: %s' % source_note)

                # Create InstitutionHistoricalRelationship record
                if not self.dry_run:
                    InstitutionHistoricalRelationship.objects.create(
                        institution_source=source_institution,
                        institution_target=target_institution,
                        relationship_type=deqar_event_type,
                        relationship_date="%s-01-01" % date['value'] if date['value'] else None,
                        relationship_note=source_note
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
            event_orgreg_id = self._get_value(rel, 'ID')
            event_type = str(self._get_value(rel, 'TYPE'))
            date_from = self._get_date_value(rel, 'STARTYEAR', default=None)
            date_to = self._get_date_value(rel, 'ENDYEAR', default=None)

            source_note = 'OrgReg-%s-%s %s' % (
                datetime.now().year, self._get_value(rel, 'ID'), self._get_value(rel, 'NOTES')
            )

            action = 'skip'

            try:
                parent_institution = Institution.objects.get(eter__eter_id=entity2)
            except ObjectDoesNotExist:
                self.report.add_report_line("%s**WARNING - Parent Institution doesn't exist with OrgReg ID [%s]. Skipping.%s"
                                            % (self.colours['WARNING'],
                                               entity2,
                                               self.colours['END']))
                return
            except MultipleObjectsReturned:
                self.report.add_report_line("%s**ERROR - Multiple Parent Institution exist with OrgReg ID [%s]. Skipping.%s"
                                            % (self.colours['ERROR'],
                                               entity2,
                                               self.colours['END']))
                return

            try:
                child_institution = Institution.objects.get(eter__eter_id=entity1)
            except ObjectDoesNotExist:
                self.report.add_report_line("%s**WARNING - Child Institution doesn't exist with OrgReg ID [%s]. Skipping.%s"
                                            % (self.colours['WARNING'],
                                               entity1,
                                               self.colours['END']))
                return
            except MultipleObjectsReturned:
                self.report.add_report_line("%s**ERROR - Multiple Child Institution exist with OrgReg ID [%s]. Skipping.%s"
                                            % (self.colours['ERROR'],
                                               entity1,
                                               self.colours['END']))
                return

            try:
                ihr = InstitutionHierarchicalRelationship.objects.get(
                    relationship_note__iregex=r'^\s*OrgReg-[0-9]{4}-%s' % event_orgreg_id
                )
                action = 'update'
            except MultipleObjectsReturned:
                self.report.add_report_line(
                    "%s**ERROR - More than one InstitutionHierarchicalRelationship record exists with the "
                    "same OrgReg ID [%s]. Skipping.%s"
                    % (self.colours['ERROR'],
                       event_orgreg_id,
                       self.colours['END']))
                return
            except ObjectDoesNotExist:
                action = 'add'

            if event_type in map.keys():
                deqar_event_type = InstitutionHierarchicalRelationshipType.objects.get(pk=map[event_type])
            else:
                self.report.add_report_line("%s**ERROR - Matching EventType can't be found [%s]. Skipping.%s"
                                            % (self.colours['ERROR'],
                                               event_type,
                                               self.colours['END']))
                return

            if action == 'update':
                values_to_update = {
                    'parent': self._compare_data(ihr.institution_parent, parent_institution),
                    'child': self._compare_data(ihr.institution_child, child_institution),
                    'type': self._compare_data(ihr.relationship_type, deqar_event_type),
                    'valid_from': self._compare_date_data(ihr.valid_from, date_from, '%s-01-01'),
                    'valid_to': self._compare_date_data(ihr.valid_to, date_to, '%s-12-31'),
                }

                if self._check_update(values_to_update):
                    self.report.add_report_line('**UPDATE - HISTORICAL RELATIONSHIP')
                    self.report.add_report_line('  Parent: %s' % values_to_update['parent']['log'])
                    self.report.add_report_line('  Child: %s' % values_to_update['child']['log'])
                    self.report.add_report_line('  Relationship Type: %s' % values_to_update['type']['log'])
                    self.report.add_report_line('  Date From: %s' % values_to_update['valid_from']['log'])
                    self.report.add_report_line('  Date To: %s' % values_to_update['valid_to']['log'])
                    self.report.add_report_line('  Source Note: %s' % source_note)

                    # Update InstitutionHierarchicalRelationship record
                    if not self.dry_run:
                        ihr.institution_parent = values_to_update['parent']['value']
                        ihr.institution_child = values_to_update['child']['value']
                        ihr.relationship_type = values_to_update['type']['value']
                        ihr.valid_from = values_to_update['valid_from']['value']
                        ihr.valid_to = values_to_update['valid_to']['value']
                        ihr.relationship_note = source_note
                        ihr.save()

            elif action == 'add':
                if date_from['key'] == 'm':
                    df = None
                else:
                    df = "%s-01-01" % date_from['value'] if date_from['value'] else None

                if date_to['key'] == 'm':
                    dt = None
                else:
                    dt = "%s-12-31" % date_from['value'] if date_from['value'] else None

                self.report.add_report_line('**ADD - HIERARCHICAL RELATIONSHIP')
                self.report.add_report_line('  Parent: %s' % parent_institution.eter)
                self.report.add_report_line('  Child: %s' % child_institution.eter)
                self.report.add_report_line('  Relationship Type: %s' % deqar_event_type)
                self.report.add_report_line('  Date From: %s' % df)
                self.report.add_report_line('  Date To: %s' % dt)
                self.report.add_report_line('  Source: %s' % source_note)

                # Create InstitutionHierarchicalRelationship record
                if not self.dry_run:
                    InstitutionHierarchicalRelationship.objects.create(
                        institution_parent=parent_institution,
                        institution_child=child_institution,
                        relationship_type=deqar_event_type,
                        valid_from=df,
                        valid_to=dt,
                        relationship_note=source_note
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
        if 'v' in values_dict[key].keys():
            return values_dict[key]['v'] if values_dict[key]['v'] else default
        else:
            return default

    def _get_date_value(self, values_dict, key, default=''):
        if 'v' in values_dict[key].keys():
            return {
                'key': 'v',
                'value': values_dict[key]['v'] if values_dict[key]['v'] else default
            }
        if 'c' in values_dict[key].keys():
            if values_dict[key]['c'] == 'a':
                return {
                    'key': 'a',
                    'value': None
                }
            if values_dict[key]['c'] == 'm':
                return {
                    'key': 'm',
                    'value': int(datetime.now().year)
                }
        else:
            return {
                'key': None,
                'value': default
            }

    def _compare_base_data(self, label, deqar_value, orgreg_value, fallback_value=None, color='', is_date=False):
        orgreg_val = None
        base_data = self.orgreg_record['BAS'][0]['BAS']

        if 'v' in base_data[orgreg_value].keys():
            orgreg_val = base_data[orgreg_value]['v']
        elif fallback_value:
            orgreg_val = base_data[fallback_value]['v']

        if orgreg_val:
            if deqar_value != orgreg_val:
                self.inst_update = True

                if is_date:
                    orgreg_val = "%s-01-01" % orgreg_val

                if deqar_value:
                    self.report.add_report_line(
                        '%s**UPDATE - %s: %s <-- %s%s' % (color, label, deqar_value, orgreg_val, self.colours['END']))
                    return {
                        'action': 'update',
                        'orgreg_value': orgreg_val
                    }
                else:
                    self.report.add_report_line(
                        '%s**ADD - %s: %s%s' % (color, label, orgreg_val, self.colours['END']))
                    return {
                        'action': 'add',
                        'orgreg_value': orgreg_val
                    }

        return {
            'action': 'None',
        }

    def _update_base_data(self, field, compare_data):
        if compare_data and compare_data['action'] != 'None':
            if not self.dry_run:
                setattr(self.inst, field, compare_data['orgreg_value'])

    def _compare_data(self, deqar_data, orgreg_data):
        compare = {
            'update': False,
            'value': deqar_data,
            'log': deqar_data
        }

        if deqar_data:
            if deqar_data != orgreg_data:
                compare['update'] = True
                compare['value'] = orgreg_data
                compare['log'] = "%s <- %s" % (deqar_data, orgreg_data)

        return compare

    def _compare_date_data(self, deqar_data, orgreg_data, suffix):
        compare = {
            'update': False,
            'value': deqar_data,
            'log': deqar_data
        }

        if orgreg_data['key'] != 'm':
            if orgreg_data['value'] and deqar_data:
                if deqar_data.year != orgreg_data['value']:
                    compare['update'] = True
                    orgreg_data = suffix % orgreg_data['value']
                    compare['value'] = orgreg_data
                    compare['log'] = "%s <- %s" % (deqar_data, orgreg_data)

        return compare

    def _compare_boolean_data(self, deqar_data, orgreg_data):
        compare = {
            'update': False,
            'value': deqar_data,
            'log': 'YES' if deqar_data else 'NO'
        }

        if deqar_data:
            if deqar_data != orgreg_data:
                compare['update'] = True
                compare['value'] = orgreg_data
                compare['log'] = 'NO <- YES' if orgreg_data else 'YES <- NO'

        return compare

    def _check_update(self, compare_data):
        update = False
        for key in compare_data.keys():
            if compare_data[key]['update']:
                update = True
        return update

    def _compare_identifiers(self, id_type, orgreg_id_value):
        try:
            inst_id = InstitutionIdentifier.objects.get(institution=self.inst, resource=id_type)
            compare = self._compare_base_data(id_type, inst_id.identifier, orgreg_id_value)

            # Update Identifier
            if compare['action'] != 'None':
                if not self.dry_run:
                    inst_id.identifier = compare['orgreg_value']
                    inst_id.save()

        except ObjectDoesNotExist:
            compare = self._compare_base_data(id_type, '', orgreg_id_value)

            # Create Identifier
            if compare['action'] != 'None':
                if not self.dry_run:
                    InstitutionIdentifier.objects.create(
                        institution=self.inst,
                        resource=id_type,
                        identifier=compare['orgreg_value']
                    )

        except MultipleObjectsReturned:
            self.report.add_report_line("Multiple IntitutionIdentifier object exist for institution [%s]"
                                        " and resource type [%s]." % (self.inst, id_type))