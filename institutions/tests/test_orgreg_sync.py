"""
End-to-end regression test for OrgReg synchronisation (`OrgRegSynchronizer`).

The synchroniser talks to the external OrgReg REST API over HTTP. To keep this test stable and
hermetic, we spin up a **local mock OrgReg API** (stdlib ``http.server``) on an ephemeral port inside
the test and point the synchroniser at it by overriding its (hardcoded but overridable) ``api``
attribute. We then run a full sync and compare the resulting institution -- serialized through the
public ``InstitutionDetailSerializer`` -- against an expected snapshot.
"""
import json
import threading
import requests
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from freezegun import freeze_time
from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from institutions.models import Institution
from institutions.orgreg.orgreg_synchronizer import OrgRegSynchronizer
from webapi.v2.serializers.institution_serializers import InstitutionDetailSerializer


# =================================================================================================
# TEST CASE DATA
# =================================================================================================

# --- Fixtures --------------------------------------------------------------------------------------
# Relationship-type PKs are hardcoded in the synchroniser's EVENTTYPE / LINK-TYPE maps, so the
# relationship-type fixtures must be loaded. `country` is edited to carry orgreg_eu_2_letter_code.
FIXTURES = [
    # `country` has FKs to these lists, so they must load alongside it.
    'country_qa_requirement_type', 'flag', 'permission_type', 'country',
    'institution_relationship_type',
    'institution_hierarchical_relationship_type',
    'identifier_resource',
    'institution_demo_orgreg',
]

# Freeze time so the `OrgReg-<year>-<id>` source notes the synchroniser writes are deterministic.
FROZEN_TIME = "2026-01-01"

# The OrgReg ID of the institution under test (the primary record synced and asserted on).
PRIMARY_ORGREG_ID = 'FR0076'

# OrgReg entity-details response(s), keyed by OrgReg ID. Must contain at least PRIMARY_ORGREG_ID and
# every OrgReg ID listed in RELATED_INSTITUTION_ETER_IDS whose full record the sync would fetch.
MOCK_ORGREG_RECORDS = {
    'FR0076': {
      "BAS": [
        {
          "_id": "5f9318989e42f21b9e419d60",
          "updatedAt": "2026-03-19T08:17:05.706Z",
          "createdAt": "2020-10-23T17:53:28.575Z",
          "__v": 248,
          "modificationDate": "2024-04-09T09:18:56.662Z",
          "BAS": {
            "ENTITYID": {
              "v": "FR0076"
            },
            "COUNTRY": {
              "v": "FR"
            },
            "ENTITYNAME": {
              "v": "Grenoble institute of technology"
            },
            "ENTITYSYNONYM": {
              "v": None
            },
            "FOUNDYEAR": {
              "v": 1900
            },
            "NOTESFOUNDYEAR": {
              "v": "first creation of engineering schools in 1900, progressively linked to the university, and separated in 1970 with the creation after loi Faure of the 3 national polytechnic institutes in Grenoble, Toulouse and Nancy"
            },
            "LEGALYEAR": {
              "c": "m"
            },
            "NOTESLEGALYEAR": {
              "v": None
            },
            "ANCESTYEAR": {
              "c": "m"
            },
            "NOTESANCESTYEAR": {
              "v": None
            },
            "ENTITYCLOSUREYEAR": {
              "c": "a"
            },
            "NOTESENTITYCLOSURE": {
              "v": None
            },
            "WEBSITE": {
              "v": "http://www.grenoble-inp.fr/"
            },
            "NOTESWEBSITE": {
              "v": None
            },
            "INSTCONTACT": {
              "v": None
            },
            "WIKIPEDIA": {
              "v": "https://en.wikipedia.org/wiki/Grenoble_Institute_of_Technology"
            },
            "NATID": {
              "v": "0381912X"
            },
            "RORID": {
              "v": "https://ror.org/05sbt2524"
            },
            "WHEDID": {
              "v": "IAU-019745-008108"
            },
            "DEQARID": {
              "v": "DEQARINST0962"
            },
            "ERASMUSCODE1420": {
              "v": "F  GRENOBL22"
            },
            "ERASMUSCODE2127": {
              "v": "F  GRENOBL22"
            },
            "CHANGES": {
              "v": None
            }
          },
          "creationDate": "2020-10-23T17:53:28.575Z"
        }
      ],
      "CHAR": [
        {
          "_id": "5f9318999e42f21b9e41a049",
          "updatedAt": "2026-03-19T08:17:09.445Z",
          "createdAt": "2020-10-23T17:53:29.366Z",
          "__v": 228,
          "modificationDate": "2021-11-22T17:28:25.075Z",
          "BAS": {
            "ENTITYID": {
              "v": "FR0076"
            }
          },
          "CHAR": {
            "CHARID": {
              "v": "CHARFR0076-1"
            },
            "INSTNAME": {
              "v": "Grenoble INP"
            },
            "INSTNAMEENGL": {
              "v": "Grenoble institute of technology"
            },
            "ACRONYM": {
              "c": "m"
            },
            "CHARSTARTYEAR": {
              "c": "m"
            },
            "NOTESCHARSTARTYEAR": {
              "v": None
            },
            "CHARENDYEAR": {
              "v": 2020
            },
            "NOTESCHARENDYEAR": {
              "v": None
            },
            "CHARCOUNTRYESTABL": {
              "v": "FR"
            },
            "CHARLEVEL": {
              "v": 2
            },
            "CHARTYPE": [
              {
                "v": 1
              }
            ],
            "CHANGES": {
              "v": None
            }
          },
          "creationDate": "2020-10-23T17:53:29.366Z"
        },
        {
          "_id": "619bd24ad605f50004091e4a",
          "BAS": {
            "ENTITYID": {
              "v": "FR0076"
            }
          },
          "CHAR": {
            "CHARID": {
              "v": "CHARFR0076-2"
            },
            "INSTNAME": {
              "v": "Grenoble INP"
            },
            "INSTNAMEENGL": {
              "v": "Grenoble institute of technology"
            },
            "ACRONYM": {
              "c": "m"
            },
            "CHARSTARTYEAR": {
              "v": 2020
            },
            "NOTESCHARSTARTYEAR": {
              "v": "Became component of FR0367"
            },
            "CHARENDYEAR": {
              "c": "a"
            },
            "NOTESCHARENDYEAR": {
              "v": None
            },
            "CHARCOUNTRYESTABL": {
              "v": "FR"
            },
            "CHARLEVEL": {
              "v": 3
            },
            "CHARTYPE": [
              {
                "v": 1
              }
            ],
            "CHANGES": {
              "v": None
            }
          },
          "modificationDate": "2021-11-22T17:24:26.032Z",
          "creationDate": "2021-11-22T17:24:26.032Z",
          "createdAt": "2021-11-22T17:24:26.032Z",
          "updatedAt": "2026-03-19T08:17:09.447Z",
          "__v": 156
        }
      ],
      "DEMO": [
        {
          "_id": "619bd24cd605f50004092ce1",
          "DEMO": {
            "EVENTID": {
              "v": "DEMOFR093"
            },
            "PARENTID": {
              "v": "FR0884"
            },
            "CHILDID": {
              "v": "FR0076"
            },
            "EVENTYEAR": {
              "v": 2020
            },
            "EVENTTYPE": {
              "v": 5
            },
            "NOTES": {
              "v": "Integration as a component of FR0076"
            },
            "CHANGES": {
              "v": None
            },
            "PARENTNAMEENGL": {
              "v": "Ecole polytechnique universitaire Grenoble Alpes"
            },
            "CHILDNAMEENGL": {
              "v": "Grenoble institute of technology"
            }
          },
          "modificationDate": "2021-11-22T17:24:28.846Z",
          "creationDate": "2021-11-22T17:24:28.846Z",
          "createdAt": "2021-11-22T17:24:28.846Z",
          "updatedAt": "2026-03-19T08:17:13.808Z",
          "__v": 158
        }
      ],
      "LINK": [
        {
          "_id": "5f9318fb9e42f21b9e41a8ea",
          "updatedAt": "2026-03-19T08:17:14.192Z",
          "createdAt": "2020-10-23T17:55:07.660Z",
          "__v": 232,
          "modificationDate": "2020-12-21T18:35:55.112Z",
          "LINK": {
            "ID": {
              "v": "LINKFR062"
            },
            "ENTITY1ID": {
              "v": "FR0076"
            },
            "ENTITY2ID": {
              "v": "FR0077"
            },
            "STARTYEAR": {
              "v": 2009
            },
            "ENDYEAR": {
              "c": "a"
            },
            "TYPE": {
              "v": 1
            },
            "NOTES": {
              "v": "Membership to Community of universities (COMUE)"
            },
            "CHANGES": {
              "v": None
            },
            "ENTITY1NAMEENGL": {
              "v": "Grenoble institute of technology"
            },
            "ENTITY2NAMEENGL": {
              "v": "Communauté Université Grenoble-Alpes"
            }
          },
          "creationDate": "2020-10-23T17:55:07.660Z"
        },
        {
          "_id": "60a52442ca1ed6000444f328",
          "LINK": {
            "ID": {
              "v": "LINKFR668"
            },
            "ENTITY1ID": {
              "v": "FR0076"
            },
            "ENTITY2ID": {
              "v": "FR0973"
            },
            "STARTYEAR": {
              "v": 2008
            },
            "ENDYEAR": {
              "c": "a"
            },
            "TYPE": {
              "v": 1
            },
            "NOTES": {
              "v": "Component of Grenoble institute of technology"
            },
            "CHANGES": {
              "v": None
            },
            "ENTITY1NAMEENGL": {
              "v": "Grenoble institute of technology"
            },
            "ENTITY2NAMEENGL": {
              "v": "Ecole nationale supérieure en systèmes avancés et réseaux"
            }
          },
          "modificationDate": "2021-05-19T14:44:18.296Z",
          "creationDate": "2021-05-19T14:44:18.226Z",
          "createdAt": "2021-05-19T14:44:18.227Z",
          "updatedAt": "2026-03-19T08:17:16.279Z",
          "__v": 220
        },
        {
          "_id": "619bd24fd605f50004093e13",
          "LINK": {
            "ID": {
              "v": "LINKFR700"
            },
            "ENTITY1ID": {
              "v": "FR0076"
            },
            "ENTITY2ID": {
              "v": "FR0367"
            },
            "STARTYEAR": {
              "v": 2020
            },
            "ENDYEAR": {
              "c": "a"
            },
            "TYPE": {
              "v": 1
            },
            "NOTES": {
              "v": "Component of EPE université Grenoble Alpes"
            },
            "CHANGES": {
              "v": None
            },
            "ENTITY1NAMEENGL": {
              "v": "Grenoble institute of technology"
            },
            "ENTITY2NAMEENGL": {
              "v": "EPE université Grenoble Alpes"
            }
          },
          "modificationDate": "2021-11-22T17:24:31.497Z",
          "creationDate": "2021-11-22T17:24:31.497Z",
          "createdAt": "2021-11-22T17:24:31.498Z",
          "updatedAt": "2026-03-19T08:17:16.398Z",
          "__v": 156
        }
      ],
      "LOCAT": [
        {
          "_id": "5f9318a19e42f21b9e41a3cc",
          "updatedAt": "2026-03-19T08:17:17.068Z",
          "createdAt": "2020-10-23T17:53:37.038Z",
          "__v": 228,
          "modificationDate": "2022-11-16T09:19:47.637Z",
          "BAS": {
            "ENTITYID": {
              "v": "FR0076"
            }
          },
          "LOCAT": {
            "LOCATID": {
              "v": "LOCATFR0076-1"
            },
            "STARTYEAR": {
              "v": 1892
            },
            "ENDYEAR": {
              "c": "a"
            },
            "COORDLAT": {
              "v": 45.191182
            },
            "COORDLON": {
              "v": 5.717299
            },
            "LEGALSEAT": {
              "v": 1
            },
            "LOCATCOUNTRY": {
              "v": "FR"
            },
            "SUBCOUNTRY": {
              "c": "a"
            },
            "CITY": {
              "v": "Grenoble"
            },
            "POSTCODE": {
              "v": "38031"
            },
            "NUTS3": {
              "v": "FRK24"
            },
            "NOTESREG": {
              "v": "identificatif de la commune:38185"
            },
            "CHANGES": {
              "v": None
            },
            "INSTNAMEENGL": {
              "v": "Grenoble institute of technology"
            }
          },
          "creationDate": "2020-10-23T17:53:37.038Z"
        },
        {
          "_id": "5f9318a19e42f21b9e41a3cd",
          "updatedAt": "2026-03-19T08:17:17.070Z",
          "createdAt": "2020-10-23T17:53:37.092Z",
          "__v": 228,
          "modificationDate": "2022-11-16T09:19:47.645Z",
          "BAS": {
            "ENTITYID": {
              "v": "FR0076"
            }
          },
          "LOCAT": {
            "LOCATID": {
              "v": "LOCATFR0076-2"
            },
            "STARTYEAR": {
              "v": 2012
            },
            "ENDYEAR": {
              "c": "a"
            },
            "COORDLAT": {
              "v": 44.9191742141
            },
            "COORDLON": {
              "v": 4.9166453299
            },
            "LEGALSEAT": {
              "v": 0
            },
            "LOCATCOUNTRY": {
              "v": "FR"
            },
            "SUBCOUNTRY": {
              "c": "a"
            },
            "CITY": {
              "v": "Valence"
            },
            "POSTCODE": {
              "v": "26902"
            },
            "NUTS3": {
              "v": "FRK23"
            },
            "NOTESREG": {
              "v": "identificatif de la commune:38185"
            },
            "CHANGES": {
              "v": None
            },
            "INSTNAMEENGL": {
              "v": "Grenoble institute of technology"
            }
          },
          "creationDate": "2020-10-23T17:53:37.092Z"
        }
      ]
    }
}

# eter_ids of institutions the primary record's DEMO/LINK relationships point to. These are created
# as bare stubs in setUp so relationship sync can resolve them (otherwise it silently skips).
#
# Alternatively, create related institutions' records in the fixture.
RELATED_INSTITUTION_ETER_IDS = [
]

# Expected `InstitutionDetailSerializer(inst).data`, round-tripped through JSON (see the assertion).
EXPECTED_SERIALIZED = {
  "id": 962,
  "eter_id": "FR0076",
  "identifiers": [
    {
      "identifier": "F  GRENOBL22",
      "agency": None,
      "resource": "Erasmus",
      "identifier_valid_from": "2026-01-01",
      "identifier_valid_to": None
    },
    {
      "identifier": "0381912X",
      "agency": None,
      "resource": "FR-ETER.BAS.NATID",
      "identifier_valid_from": "2026-01-01",
      "identifier_valid_to": None
    },
    {
      "identifier": "https://ror.org/05sbt2524",
      "agency": None,
      "resource": "ROR",
      "identifier_valid_from": "2026-01-01",
      "identifier_valid_to": None
    },
    {
      "identifier": "IAU-019745-008108",
      "agency": None,
      "resource": "WHED",
      "identifier_valid_from": "2026-01-01",
      "identifier_valid_to": None
    }
  ],
  "website_link": "http://www.grenoble-inp.fr/",
  "names": [
    {
      "name_official": "Grenoble INP",
      "name_official_transliterated": "",
      "name_english": "Grenoble institute of technology",
      "name_versions": [],
      "acronym": "",
      "name_source_note": "OrgReg-2026-CHARFR0076-1 ",
      "name_valid_to": "2020-12-31"
    },
    {
      "name_official": "Grenoble INP",
      "name_official_transliterated": "",
      "name_english": "Grenoble institute of technology",
      "name_versions": [],
      "acronym": "",
      "name_source_note": "OrgReg-2026-CHARFR0076-2 Became component of FR0367",
      "name_valid_to": None
    }
  ],
  "countries": [
    {
      "country": {
        "id": 60,
        "name_english": "France",
        "iso_3166_alpha2": "FR",
        "iso_3166_alpha3": "FRA",
        "ehea_is_member": True,
        "eqar_governmental_member_start": "2008-02-28",
        "qa_requirements": [],
        "qa_requirement_note": "",
        "external_QAA_is_permitted": "yes",
        "external_QAA_note": "",
        "eligibility": "",
        "conditions": "",
        "recognition": "",
        "european_approach_is_permitted": "no",
        "european_approach_note": "",
        "has_full_institution_list": False,
        "ehea_key_commitment": "no",
        "general_note": "",
        "qaa_regulations": [],
        "report_count": 0,
        "institution_count": 0,
        "historical_data": []
      },
      "city": "Valence",
      "lat": 44.9191742141,
      "long": 4.9166453299,
      "country_source": "",
      "country_valid_from": "2012-01-01",
      "country_valid_to": None,
      "country_verified": False
    },
    {
      "country": {
        "id": 60,
        "name_english": "France",
        "iso_3166_alpha2": "FR",
        "iso_3166_alpha3": "FRA",
        "ehea_is_member": True,
        "eqar_governmental_member_start": "2008-02-28",
        "qa_requirements": [],
        "qa_requirement_note": "",
        "external_QAA_is_permitted": "yes",
        "external_QAA_note": "",
        "eligibility": "",
        "conditions": "",
        "recognition": "",
        "european_approach_is_permitted": "no",
        "european_approach_note": "",
        "has_full_institution_list": False,
        "ehea_key_commitment": "no",
        "general_note": "",
        "qaa_regulations": [],
        "report_count": 0,
        "institution_count": 0,
        "historical_data": []
      },
      "city": "Grenoble",
      "lat": 45.191182,
      "long": 5.717299,
      "country_source": "",
      "country_valid_from": "1892-01-01",
      "country_valid_to": None,
      "country_verified": True
    }
  ],
  "founding_date": "1900-01-01",
  "closure_date": None,
  "historical_relationships": [
    {
      "institution": {
        "id": 7014,
        "eter_id": "FR0884",
        "url": "http://testserver/webapi/v2/browse/institutions/7014/",
        "name_primary": "Ecole polytechnique universitaire Grenoble Alpes",
        "name_sort": "Ecole polytechnique universitaire Grenoble Alpes",
        "website_link": "https://www.polytech-grenoble.fr/",
        "countries": []
      },
      "relationship_type": "succeeded",
      "relationship_date": "2020-01-01"
    }
  ],
  "hierarchical_relationships": {
    "includes": [],
    "part_of": [
      {
        "institution": {
          "id": 963,
          "eter_id": "FR0077",
          "url": "http://testserver/webapi/v2/browse/institutions/963/",
          "name_primary": "Communauté Université Grenoble-Alpes",
          "name_sort": "Communauté Université Grenoble-Alpes",
          "website_link": "http://www.grenoble-univ.fr/",
          "countries": []
        },
        "relationship_type": "consortium",
        "valid_from": "2009-01-01",
        "valid_to": None
      },
      {
        "institution": {
          "id": 7026,
          "eter_id": "FR0973",
          "url": "http://testserver/webapi/v2/browse/institutions/7026/",
          "name_primary": "Ecole nationale supérieure en systèmes avancés et réseaux",
          "name_sort": "Ecole nationale supérieure en systèmes avancés et réseaux",
          "website_link": "https://esisar.grenoble-inp.fr/fr/l-ecole",
          "countries": [
            {
              "country": "France",
              "city": "Valence",
              "lat": 44.917222,
              "long": 4.913611,
              "country_verified": True
            }
          ]
        },
        "relationship_type": "consortium",
        "valid_from": "2008-01-01",
        "valid_to": None
      },
      {
        "institution": {
          "id": 7597,
          "eter_id": "FR0367",
          "url": "http://testserver/webapi/v2/browse/institutions/7597/",
          "name_primary": "EPE université Grenoble Alpes",
          "name_sort": "EPE université Grenoble Alpes",
          "website_link": "https://www.univ-grenoble-alpes.fr/english/",
          "countries": [
            {
              "country": "France",
              "city": "Saint-Martin-d'Hères",
              "lat": 45.189444,
              "long": 5.77,
              "country_verified": True
            }
          ]
        },
        "relationship_type": "consortium",
        "valid_from": "2020-01-01",
        "valid_to": None
      }
    ]
  },
  "meili_filters": {
    "reports": [
      "institutions.id = 962",
      "platforms.id = 962",
      "institutions.id = 7014 AND valid_to_calculated >= 1577836800"
    ],
    "programmes": [
      "institutions = 962",
      "platforms = 962",
      "institutions = 7014 AND report.valid_to_calculated >= 1577836800"
    ]
  },
  "qf_ehea_levels": [],
  "is_other_provider": False,
  "is_orgreg_alliance": False,
  "organization_type": None,
  "source_of_information": None,
  "historical_data": []
}

# =================================================================================================

class _OrgRegMockHandler(BaseHTTPRequestHandler):
    """Serves the two OrgReg endpoints the synchroniser calls, from MOCK_ORGREG_RECORDS."""

    def _send(self, status, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # GET {api}entity-details/<orgreg_id>  -> 200 + the full record (404 if unknown)
        prefix = '/entity-details/'
        if self.path.startswith(prefix):
            orgreg_id = self.path[len(prefix):].strip('/')
            record = MOCK_ORGREG_RECORDS.get(orgreg_id)
            if record is not None:
                self._send(200, record)
            else:
                self._send(404, {'error': 'not found', 'id': orgreg_id})
        else:
            self._send(404, {'error': 'unknown path', 'path': self.path})

    def do_POST(self):
        # POST {api}organizations/query -> 201 + {"entities": [...]} built from the mock records.
        length = int(self.headers.get('Content-Length', 0))
        if length:
            self.rfile.read(length)
        if self.path.endswith('/organizations/query'):
            entities = [
                {'BAS': {'ENTITYID': {'v': orgreg_id}}}
                for orgreg_id in MOCK_ORGREG_RECORDS.keys()
            ]
            self._send(201, {'entities': entities})
        else:
            self._send(404, {'error': 'unknown path', 'path': self.path})

    def log_message(self, format, *args):  # noqa: A002 - silence stdlib request logging in tests
        pass


class OrgRegSyncTest(TestCase):
    fixtures = FIXTURES
    maxDiff = None

    def setUp(self):
        # Spin up the local mock OrgReg API on an ephemeral port in a daemon thread.
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), _OrgRegMockHandler)
        self.port = self.server.server_address[1]
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

        # Pre-create the related institutions referenced by DEMO/LINK relationships.
        for eter_id in RELATED_INSTITUTION_ETER_IDS:
            Institution.objects.get_or_create(
                eter_id=eter_id, defaults={'website_link': 'http://example.com'}
            )

        # Synchroniser pointed at the mock server. dry_run=False so records are actually written.
        self.sync = OrgRegSynchronizer(dry_run=False)
        self.sync.api = 'http://127.0.0.1:%d/' % self.port

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join(timeout=5)

    def test_orgreg_mock_api(self):
        get_ok = requests.get(self.sync.api + '/entity-details/' + PRIMARY_ORGREG_ID)
        self.assertEqual(get_ok.status_code, 200)
        get_404 = requests.get(self.sync.api + '/entity-details/XYZ4711')
        self.assertEqual(get_404.status_code, 404)
        get_404 = requests.get(self.sync.api + '/unknown-path-entirely')
        self.assertEqual(get_404.status_code, 404)
        post_ok = requests.post(self.sync.api + '/organizations/query')
        self.assertEqual(post_ok.status_code, 201)
        post_404 = requests.post(self.sync.api + '/some-wrong-path')
        self.assertEqual(post_404.status_code, 404)

    @freeze_time(FROZEN_TIME)
    def test_sync_institution_matches_expected(self):
        # Collect the ID (hits the mock entity-details endpoint) and run the full sync.
        self.assertTrue(
            self.sync.collect_orgreg_ids_by_institution(PRIMARY_ORGREG_ID),
            "mock OrgReg API did not return the primary record",
        )
        self.sync.run()

        inst = Institution.objects.get(eter_id=PRIMARY_ORGREG_ID)

        # InstitutionDetailSerializer emits HyperlinkedIdentityField URLs (needing a request in the
        # context) and its HistoryFilteredListSerializer reads request.query_params, so the request
        # must be a DRF Request, not a bare WSGIRequest. Under the test client the host is
        # `testserver`, so the URLs are stable.
        context = {'request': Request(APIRequestFactory().get('/'))}
        data = InstitutionDetailSerializer(inst, context=context).data

        # Round-trip through JSON so OrderedDict / date / Decimal values compare cleanly against the
        # plain-dict snapshot pasted into EXPECTED_SERIALIZED.
        self.assertEqual(json.loads(json.dumps(data)), EXPECTED_SERIALIZED)

