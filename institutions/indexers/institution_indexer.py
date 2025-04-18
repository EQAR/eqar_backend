import json
import re

import pysolr
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from agencies.models import AgencyActivityType
from institutions.models import Institution
from reports.models import Report


class InstitutionIndexer:
    """
    Class to index Institution and their corresponding Report records to Solr.
    """

    def __init__(self, institution_id):
        self.institution_id = institution_id
        self.institution = None
        self.solr_core = getattr(settings, "SOLR_CORE_INSTITUTIONS", "deqar-institutions")
        self.solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), self.solr_core)
        self.solr = pysolr.Solr(self.solr_url, always_commit=True)
        self.doc = {
            # Display fields
            'id': None,
            'deqar_id': None,
            'eter_id': None,
            'name_primary': None,
            'name_select_display': None,
            'name_official_display': None,
            'national_identifier': None,
            'website_link': None,
            'founding_date': None,
            'closure_date': None,
            'place': [],
            'hierarchical_relationships': {
                'part_of': [],
                'includes': []
            },
            'qf_ehea_level': [],

            # Search fields
            'deqar_id_search': None,
            'name_english': [],
            'acronym_search': [],
            'name_official_transliterated': [],
            'name_official': [],
            'name_version': [],
            'name_version_transliterated': [],
            'city': [],
            'country': [],

            # ID Filter fields
            'agency_id': [],
            'activity_id': [],
            'activity_type_id': [],
            'country_id': [],
            'status_id': [],
            'qf_ehea_level_id': [],

            # Sort fields
            'name_sort': None,
            'deqar_id_sort': None,
            'eter_id_sort': None,

            # Aggregated search fields
            'aggregated_name_english': [],
            'aggregated_name_official': [],
            'aggregated_name_official_transliterated': [],
            'aggregated_name_version': [],
            'aggregated_name_version_transliterated': [],
            'aggregated_city': [],
            'aggregated_country': [],

            # Facet fields
            'reports_agencies': [],
            'activity_facet': [],
            'activity_type_facet': [],
            'country_facet': [],
            'status_facet': [],
            'qf_ehea_level_facet': [],
            'crossborder_facet': [],
            'other_provider_facet': False,

            # Report indicator
            'has_report': False,
        }

    def index(self):
        self._get_institution()
        self._index_main_institution()
        self._index_hierarchical_institutions()
        self._index_reports()
        self._store_json()
        self._remove_duplicates()
        self._remove_empty_keys()
        try:
            self.solr.add([self.doc])
            print('Indexed Institution No. %s!' % self.doc['id'])
        except pysolr.SolrError as e:
            print('Error with Institution No. %s! Error: %s' % (self.doc['id'], e))

    def delete(self):
        self.solr.delete(self.institution_id)
        print('Deleted Institution No. %s!' % self.institution_id)
        self.solr.commit()

    def _get_institution(self):
        self.institution = Institution.objects.get(pk=self.institution_id)

    def _index_main_institution(self):
        # Index display fields
        self.doc['id'] = self.institution.id
        self.doc['deqar_id'] = self.institution.deqar_id
        self.doc['deqar_id_search'] = self.institution.deqar_id
        self.doc['deqar_id_sort'] = self.institution.id
        self.doc['name_primary'] = self.institution.name_primary.strip()
        self.doc['national_identifier'] = self.institution.national_identifier
        self.doc['website_link'] = self.institution.website_link.strip()

        if self.institution.is_other_provider:
            self.doc['other_provider'] = True
            self.doc['other_provider_facet'] = True
        else:
            self.doc['other_provider'] = False
            self.doc['other_provider_facet'] = False

        if self.institution.founding_date:
            self.doc['founding_date'] = str(self.institution.founding_date)

        if self.institution.closure_date:
            self.doc['closure_date'] = str(self.institution.closure_date)

        select_display = self.institution.name_primary.strip()
        if self.institution.eter_id:
            self.doc['eter_id'] = self.institution.eter_id
            self.doc['eter_id_sort'] = self.institution.eter_id
            select_display += ' (%s)' % self.institution.eter_id
        self.doc['name_select_display'] = select_display

        # Index name_display
        name = self.institution.name_primary
        for iname in self.institution.institutionname_set.all():
            if not iname.name_valid_to:
                if iname.name_official != self.institution.name_primary:
                    name += " / " + iname.name_official
                if iname.acronym:
                    name += " (" + iname.acronym + ')'
        self.doc['name_display'] = name

        # Index name_sort
        self.doc['name_sort'] = re.sub(r'[\W_]+', u'', self.institution.name_sort.strip(), flags=re.UNICODE)

        # Index name versions
        for iname in self.institution.institutionname_set.all():
            self.doc['name_official'].append(iname.name_official.strip())
            self.doc['name_official_transliterated'].append(iname.name_official_transliterated.strip())
            self.doc['name_english'].append(iname.name_english.strip())

            if not iname.name_valid_to or iname.name_valid_to == '':
                self.doc['name_official_display'] = iname.name_official.strip()

            # Index acronym
            if iname.acronym:
                self.doc['acronym_search'].append(iname.acronym)

            for iname_version in iname.institutionnameversion_set.all():
                self.doc['name_version'].append(iname_version.name.strip())
                self.doc['name_version_transliterated'].append(iname_version.transliteration.strip())

        self.doc['name_official'] = list(filter(None, self.doc['name_official']))
        self.doc['name_official_transliterated'] = list(filter(None, self.doc['name_official_transliterated']))
        self.doc['name_english'] = list(filter(None, self.doc['name_english']))
        self.doc['name_version'] = list(filter(None, self.doc['name_version']))
        self.doc['name_version_transliterated'] = list(filter(None, self.doc['name_version_transliterated']))

        # Index places
        for icountry in self.institution.institutioncountry_set.iterator():
            self.doc['place'].append({
                'country': icountry.country.name_english.strip(),
                'city': icountry.city.strip() if icountry.city else None,
                'country_verified': icountry.country_verified,
                'lat': icountry.lat,
                'long': icountry.long
            })
            self.doc['country'].append(icountry.country.name_english.strip())
            self.doc['country_id'].append(icountry.country.id)
            if icountry.city:
                self.doc['city'].append(icountry.city.strip())

        countries = list(dict.fromkeys(self.doc['country']))
        country_ids = list(dict.fromkeys(self.doc['country_id']))
        cities = list(dict.fromkeys(self.doc['city']))

        self.doc['country'] = countries
        self.doc['country_facet'] = countries

        self.doc['country_id'] = country_ids
        self.doc['city'] = cities

        # Index QF-EHEA level
        for iqfehealevel in self.institution.institutionqfehealevel_set.iterator():
            self.doc['qf_ehea_level'].append(iqfehealevel.qf_ehea_level.level.strip())
            self.doc['qf_ehea_level_id'].append(iqfehealevel.qf_ehea_level.id)
            self.doc['qf_ehea_level_facet'].append(iqfehealevel.qf_ehea_level.level.strip())

        self.doc['qf_ehea_level'] = list(filter(None, self.doc['qf_ehea_level']))
        self.doc['qf_ehea_level_facet'] = list(filter(None, self.doc['qf_ehea_level_facet']))

    def _index_hierarchical_institutions(self):
        # Index children
        includes = []
        for related_institution in self.institution.relationship_parent.iterator():
            includes.append({
                'name_primary': related_institution.institution_child.name_primary,
                'website_link': related_institution.institution_child.website_link,
                'relationship_type': related_institution.relationship_type.type
                if related_institution.relationship_type else None,
                'valid_from': str(related_institution.valid_from)
                if related_institution.valid_from else None,
                'valid_to': str(related_institution.valid_to)
                if related_institution.valid_to else None
            })
            self._index_related_institution(related_institution.institution_child)
        self.doc['hierarchical_relationships']['includes'] = includes

        # Index parents
        part_of = []
        for related_institution in self.institution.relationship_child.iterator():
            part_of.append({
                'name_primary': related_institution.institution_parent.name_primary,
                'website_link': related_institution.institution_parent.website_link,
                'relationship_type': related_institution.relationship_type.type
                if related_institution.relationship_type else None,
                'valid_from': str(related_institution.valid_from)
                if related_institution.valid_from else None,
                'valid_to': str(related_institution.valid_to)
                if related_institution.valid_to else None
            })
            self._index_related_institution(related_institution.institution_parent)
        self.doc['hierarchical_relationships']['part_of'] = part_of

    def _index_related_institution(self, related_institution):
        # Index name versions
        aggregated_name_official = self.doc['aggregated_name_official']
        aggregated_name_official_transliterated = self.doc['aggregated_name_official_transliterated']
        aggregated_name_english = self.doc['aggregated_name_english']
        aggregated_name_version = self.doc['aggregated_name_version']
        aggregated_name_version_transliterated = self.doc['aggregated_name_version_transliterated']

        for iname in related_institution.institutionname_set.iterator():
            aggregated_name_official.append(iname.name_official.strip())
            aggregated_name_official_transliterated.append(iname.name_official_transliterated.strip())
            aggregated_name_english.append(iname.name_english.strip())

            for iname_version in iname.institutionnameversion_set.iterator():
                aggregated_name_version.append(iname_version.name.strip())
                aggregated_name_version_transliterated.append(iname_version.transliteration.strip())

        self.doc['aggregated_name_official'] = list(filter(None, aggregated_name_official))
        self.doc['aggregated_name_official_transliterated'] = list(
            filter(None, aggregated_name_official_transliterated))
        self.doc['aggregated_name_english'] = list(filter(None, aggregated_name_english))
        self.doc['aggregated_name_version'] = list(filter(None, aggregated_name_version))
        self.doc['aggregated_name_version_transliterated'] = list(filter(None, aggregated_name_version_transliterated))

    def _remove_duplicates(self):
        for k, v in self.doc.items():
            if isinstance(v, list):
                self.doc[k] = list(set(v))

    def _remove_empty_keys(self):
        new_doc = {k: v for k, v in self.doc.items() if v}
        self.doc.clear()
        self.doc.update(new_doc)

    def _store_json(self):
        self.doc['place'] = json.dumps(self.doc['place'])
        self.doc['hierarchical_relationships'] = json.dumps(self.doc['hierarchical_relationships'])

    def _index_reports(self):
        reports = Report.objects.filter(institutions=self.institution).iterator()
        self._add_reports(reports)

    def _index_related_reports(self):
        # Index parents
        for related_institution in self.institution.relationship_parent.iterator():
            reports = Report.objects.filter(institution=related_institution.institution_child).iterator()
            self._add_reports(reports)

        # Index children
        for related_institution in self.institution.relationship_child.iterator():
            reports = Report.objects.filter(institution=related_institution.institution_parent).iterator()
            self._add_reports(reports)

    def _add_reports(self, reports):
        for report in reports:
            self.doc['has_report'] = True
            self.doc['reports_agencies'].append(report.agency.acronym_primary)
            self.doc['status_facet'].append(report.status.status)
            for activity in report.agency_esg_activities.all():
                self.doc['activity_facet'].append(activity.activity_display)

            try:
                for activity in report.agency_esg_activities.all():
                    at = AgencyActivityType.objects.get(id=activity.activity_type_id)
                    self.doc['activity_type_facet'].append(at.type)
            except ObjectDoesNotExist:
                at = None
            self.doc['crossborder_facet'].append(False)

            # Cross-border filter
            focus_countries = report.agency.agencyfocuscountry_set
            for ic in self.institution.institutioncountry_set.iterator():
                if focus_countries.filter(Q(country__id=ic.country.id) & Q(country_is_crossborder=True)):
                    self.doc['crossborder_facet'].append(True)
