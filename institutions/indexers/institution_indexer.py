import json

import pysolr
from django.conf import settings
from django.db.models import Q

from reports.models import Report


class InstitutionIndexer:
    """
    Class to index Institution and their corresponding Report records to Solr.
    """

    def __init__(self, institution):
        self.institution = institution
        self.solr_core = getattr(settings, "SOLR_CORE_INSTITUTIONS", "deqar-institutions")
        self.solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), self.solr_core)
        self.solr = pysolr.Solr(self.solr_url)
        self.doc = {
            # Display fields
            'id': None,
            'deqar_id': None,
            'eter_id': None,
            'name_primary': None,
            'name_official': [],
            'national_identifier': None,
            'website_link': None,
            'place': [],
            'hierarchical_relationships': {
                'part_of': [],
                'includes': []
            },
            'qf_ehea_level': [],

            # Search fields
            'name_english': [],
            'name_official_transliterated': [],
            'name_select_display': None,
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

            # Report indicator
            'has_report': False,
        }

    def index(self):
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

    def _index_main_institution(self):
        # Index display fields
        self.doc['id'] = self.institution.id
        self.doc['deqar_id'] = 'DEQARINST%04d' % self.institution.id
        self.doc['name_primary'] = self.institution.name_primary.strip()
        self.doc['national_identifier'] = self.institution.national_identifier
        self.doc['website_link'] = self.institution.website_link.strip()

        select_display = self.institution.name_primary.strip()
        if self.institution.eter:
            self.doc['eter_id'] = self.institution.eter.eter_id
            select_display += ' (%s)' % self.institution.eter.eter_id
        self.doc['name_select_display'] = select_display

        # Index name_sort
        self.doc['name_sort'] = self.institution.name_sort.strip()

        # Index name versions
        for iname in self.institution.institutionname_set.all():
            self.doc['name_official'].append(iname.name_official.strip())
            self.doc['name_official_transliterated'].append(iname.name_official_transliterated.strip())
            self.doc['name_english'].append(iname.name_english.strip())

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
                'lat': icountry.lat,
                'long': icountry.long
            })
            self.doc['country'].append(icountry.country.name_english.strip())
            self.doc['country_id'].append(icountry.country.id)
            if icountry.city:
                self.doc['city'].append(icountry.city.strip())


        self.doc['country'] = list(filter(None, self.doc['country']))
        self.doc['country_facet'] = list(filter(None, self.doc['country']))

        self.doc['country_id'] = list(filter(None, self.doc['country_id']))
        self.doc['city'] = list(filter(None, self.doc['city']))

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
                if related_institution.relationship_type else None
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
                if related_institution.relationship_type else None
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
            self.doc['activity_facet'].append(report.agency_esg_activity.activity_display)
            self.doc['activity_type_facet'].append(report.agency_esg_activity.activity_type.type)
            self.doc['crossborder_facet'].append(False)

            # Cross-border filter
            focus_countries = report.agency.agencyfocuscountry_set
            for ic in self.institution.institutioncountry_set.iterator():
                if focus_countries.filter(Q(country__id=ic.country.id) & Q(country_is_crossborder=True)):
                    self.doc['crossborder_facet'].append(True)
