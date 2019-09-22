



## Agency(agencies.models.Agency)

```

    List of registered EQAR agencies.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|deqar_id |integer | | | | | |
|name_primary |varchar(200) | | | |Blank | |
|acronym_primary |varchar(20) | | | |Blank | |
|contact_person |varchar(150) | | | | | |
|fax |varchar(20) | | | |Blank | |
|address |text | | | | | |
|country |integer | | |True | |FK:countries.models.Country |
|website_link |varchar(100) | | | | | |
|logo |varchar(100) | | | |Both | |
|geographical_focus |integer | | |True |Both |FK:agencies.models.AgencyGeographicalFocus |
|specialisation_note |text | | | |Blank | |
|reports_link |varchar(200) | | | |Both | |
|description_note |text | | | | | |
|is_registered |boolean | | | |Blank | |
|registration_start |date | | | | | |
|registration_valid_to |date | | | | | |
|registration_note |text | | | |Blank | |
|flag |integer | | |True | |FK:lists.models.Flag |
|flag_log |text | | | |Blank | |
|related_agencies | | | | | |M2M:agencies.models.Agency (through: agencies.models.AgencyRelationship) |


## Agency Geographical Focus(agencies.models.AgencyGeographicalFocus)

```

    List of the agency focus level.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|focus |varchar(20) | |True | | | |


## Agency Name(agencies.models.AgencyName)

```

    List of agency names/acronyms in a particular period.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|agency |integer | | |True | |FK:agencies.models.Agency |
|name_note |text | | | |Blank | |
|name_valid_to |date | | | |Both | |


## Agency Name Version(agencies.models.AgencyNameVersion)

```

    Different versions of agency names with transliteration as applicable.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|agency_name |integer | | |True | |FK:agencies.models.AgencyName |
|name |varchar(200) | | | | | |
|name_transliterated |varchar(200) | | | |Blank | |
|name_is_primary |boolean | | | |Blank | |
|acronym |varchar(20) | | | |Blank | |
|acronym_transliterated |varchar(20) | | | |Blank | |
|acronym_is_primary |boolean | | | |Blank | |


## Agency Phone(agencies.models.AgencyPhone)

```

    One or more phone numbers for each agency.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|agency |integer | | |True | |FK:agencies.models.Agency |
|phone |varchar(20) | | | | | |

Options
```
unique_together : (('agency', 'phone'),)
```


## Agency Email(agencies.models.AgencyEmail)

```

    One or more contact emails for each agency.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|agency |integer | | |True | |FK:agencies.models.Agency |
|email |varchar(50) | | | | | |

Options
```
unique_together : (('agency', 'email'),)
```


## Agency Focus Country(agencies.models.AgencyFocusCountry)

```

    List of EHEA countries where the agency has evaluated,
    accredited or audited higher education institutions or programmes.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|agency |integer | | |True | |FK:agencies.models.Agency |
|country |integer | | |True | |FK:countries.models.Country |
|country_is_official |boolean | | | |Blank | |
|country_is_crossborder |boolean | | | |Blank | |
|country_valid_from |date | | | | | |
|country_valid_to |date | | | |Both | |

Options
```
unique_together : (('agency', 'country'),)
```


## Agency ESG Activity(agencies.models.AgencyESGActivity)

```

    External quality assurance activities in the scope of the ESG.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|agency |integer | | |True | |FK:agencies.models.Agency |
|activity |varchar(500) | | | | | |
|activity_display |varchar(500) | | | |Both | |
|activity_local_identifier |varchar(100) | | | |Blank | |
|activity_description |varchar(300) | | | |Blank | |
|activity_type |integer | | |True | |FK:agencies.models.AgencyActivityType |
|reports_link |varchar(200) | | | |Both | |
|activity_valid_from |date | | | | | |
|activity_valid_to |date | | | |Both | |


## Agency Activity Type(agencies.models.AgencyActivityType)

```

    Agency activity types.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|type |varchar(30) | |True | | | |


## Agency Relationship(agencies.models.AgencyRelationship)

```

    Mergers, spin offs and other historical events which link two agencies.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|from_agency |integer | | |True | |FK:agencies.models.Agency |
|to_agency |integer | | |True | |FK:agencies.models.Agency |
|note |text | | | | | |
|date |date | | | | | |

Options
```
unique_together : (('from_agency', 'to_agency'),)
```


## Agency Membership(agencies.models.AgencyMembership)

```

    List of associations to which each agency belongs.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|agency |integer | | |True | |FK:agencies.models.Agency |
|association |integer | | |True | |FK:lists.models.Association |
|membership_valid_from |date | | | | | |
|membership_valid_to |date | | | |Both | |

Options
```
unique_together : (('agency', 'association'),)
```


## Agency EQAR Decision(agencies.models.AgencyEQARDecision)

```

    List of EQAR register decision dates for each agency with any connected reports.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|agency |integer | | |True | |FK:agencies.models.Agency |
|decision_date |date | | | | | |
|decision_type |integer | | |True | |FK:lists.models.EQARDecisionType |
|decision_file |varchar(100) | | | | | |
|decision_file_extra |varchar(100) | | | |Blank | |


## Submitting Agency(agencies.models.SubmittingAgency)

```

    List of agencies registered to submit data to DEQAR.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|agency |integer | | |True |Both |FK:agencies.models.Agency |
|external_agency |varchar(200) | | | |Blank | |
|external_agency_acronym |varchar(20) | | | |Blank | |
|registration_from |date | | | | | |
|registration_to |date | | | |Both | |


## Agency Proxy(agencies.models.AgencyProxy)

```

    List of EQAR registered agencies whose data is submitted to DEQAR by a different submitting agency.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|submitting_agency |integer | | |True | |FK:agencies.models.SubmittingAgency |
|allowed_agency |integer | | |True | |FK:agencies.models.Agency |
|proxy_from |date | | | | | |
|proxy_to |date | | | |Both | |

Options
```
unique_together : (('submitting_agency', 'allowed_agency'),)
```


## Agency Historical Field(agencies.models.AgencyHistoricalField)

```

    Name of the db_fields which can contain historical data.
    This will save changed data from named fields.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|field |varchar(50) | | | | | |


## Agency Historical Data(agencies.models.AgencyHistoricalData)

```

    The historical data that agencies change.
    Either valid from or valid to date must be filled.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|agency |integer | | |True | |FK:agencies.models.Agency |
|field |integer | | |True | |FK:agencies.models.AgencyHistoricalField |
|record_id |integer | | | |Both | |
|value |varchar(200) | | | | | |
|valid_from |date | | | |Both | |
|valid_to |date | | | |Both | |


## Country(countries.models.Country)

```

    Countries related to HE institutions, EQAR agencies and other QA activities.
    Includes information on QA requirements imposed in the country.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|iso_3166_alpha2 |varchar(2) | | | | | |
|iso_3166_alpha3 |varchar(3) | | | | | |
|name_english |varchar(100) | |True | | | |
|ehea_is_member |boolean | | | |Blank | |
|eqar_governmental_member_start |date | | | |Both | |
|qa_requirement_note |text | | | |Blank | |
|external_QAA_is_permitted |integer | | |True | |FK:lists.models.PermissionType |
|external_QAA_note |text | | | |Both | |
|eligibility |text | | | |Both | |
|conditions |text | | | |Both | |
|recognition |text | | | |Both | |
|european_approach_is_permitted |integer | | |True | |FK:lists.models.PermissionType |
|european_approach_note |text | | | |Both | |
|general_note |text | | | |Blank | |
|flag |integer | | |True | |FK:lists.models.Flag |
|flag_log |text | | | |Blank | |


## Country QA Requirement(countries.models.CountryQARequirement)

```
CountryQARequirement(id, country, qa_requirement, qa_requirement_type, qa_requirement_note, requirement_valid_from, requirement_valid_to)
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|country |integer | | |True | |FK:countries.models.Country |
|qa_requirement |varchar(200) | | | | | |
|qa_requirement_type |integer | | |True | |FK:countries.models.CountryQARequirementType |
|qa_requirement_note |text | | | |Blank | |
|requirement_valid_from |date | | | | | |
|requirement_valid_to |date | | | |Both | |


## Country QA Requirement Type(countries.models.CountryQARequirementType)

```

    Type of country requriement types.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|qa_requirement_type |varchar(200) | | | |Blank | |


## Country QAA Regulation(countries.models.CountryQAARegulation)

```

    List of QAA regulations imposed on external agencies by individual countries.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|country |integer | | |True | |FK:countries.models.Country |
|regulation |varchar(200) | | | |Blank | |
|regulation_url |varchar(200) | | | |Blank | |
|regulation_valid_from |date | | | | | |
|regulation_valid_to |date | | | |Both | |


## Country Historical Field(countries.models.CountryHistoricalField)

```

    Name of the db_fields which can contain historical data of the country.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|field |varchar(50) | | | | | |


## Country Historical Data(countries.models.CountryHistoricalData)

```

    The historical data that country change.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|country |integer | | |True | |FK:countries.models.Country |
|field |integer | | |True | |FK:countries.models.CountryHistoricalField |
|record_id |integer | | | |Both | |
|value |varchar(200) | | | | | |
|valid_from |date | | | |Both | |
|valid_to |date | | | |Both | |


## Institution(institutions.models.Institution)

```

    List of institutions reviewed or evaluated by EQAR registered agencies.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|deqar_id |varchar(25) | | | |Blank | |
|eter |integer | | |True |Both |FK:institutions.models.InstitutionETERRecord |
|name_primary |varchar(200) | | | |Blank | |
|website_link |varchar(150) | | | | | |
|founding_date |date | | | |Both | |
|closure_date |date | | | |Both | |
|national_identifier |varchar(50) | | | |Both | |
|source_note |text | | | |Blank | |
|flag |integer | | |True | |FK:lists.models.Flag |
|flag_log |text | | | |Blank | |
|name_sort |varchar(500) | | | |Blank | |
|has_report |boolean | | | |Blank | |
|other_comment |text | | | |Blank | |
|internal_note |text | | | |Blank | |
|created_at |timestamp with time zone | | | |Blank | |


## Institution Identifier(institutions.models.InstitutionIdentifier)

```

    List of other (non-ETER) identifiers for the institution and the source of the identifier.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|institution |integer | | |True | |FK:institutions.models.Institution |
|identifier |varchar(50) | | | | | |
|agency |integer | | |True |Both |FK:agencies.models.Agency |
|resource |varchar(200) | | | |Blank | |
|note |text | | | |Blank | |
|identifier_valid_from |date | | | | | |
|identifier_valid_to |date | | | |Both | |

Options
```
unique_together : (('institution', 'agency', 'resource'),)
```


## Institution Name(institutions.models.InstitutionName)

```

    List of names/acronym used for an institution in a particular period.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|institution |integer | | |True | |FK:institutions.models.Institution |
|name_official |varchar(200) | | | | | |
|name_official_transliterated |varchar(200) | | | |Blank | |
|name_english |varchar(200) | | | |Blank | |
|acronym |varchar(30) | | | |Blank | |
|name_source_note |text | | | |Blank | |
|name_valid_to |date | | | |Both | |


## Institution Name Version(institutions.models.InstitutionNameVersion)

```

    Different versions of institution names with transliteration as applicable.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|institution_name |integer | | |True | |FK:institutions.models.InstitutionName |
|name |varchar(200) | | | | | |
|transliteration |varchar(200) | | | |Blank | |
|name_version_source |varchar(20) | | | |Blank | |
|name_version_source_note |text | | | |Blank | |


## Institution Country(institutions.models.InstitutionCountry)

```

    List of countries where the institution is located.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|institution |integer | | |True | |FK:institutions.models.Institution |
|country |integer | | |True | |FK:countries.models.Country |
|city |varchar(100) | | | |Both | |
|lat |double precision | | | |Both | |
|long |double precision | | | |Both | |
|country_source |varchar(20) | | | | | |
|country_source_note |text | | | |Blank | |
|country_valid_from |date | | | | | |
|country_valid_to |date | | | |Both | |
|country_verified |boolean | | | |Blank | |


## Institution NQF Level(institutions.models.InstitutionNQFLevel)

```

    List of NQF levels that are valid for each institution.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|institution |integer | | |True | |FK:institutions.models.Institution |
|nqf_level |varchar(10) | | | | | |
|nqf_level_source |varchar(20) | | | | | |
|nqf_level_source_note |text | | | |Blank | |
|nqf_level_valid_from |date | | | | | |
|nqf_level_valid_to |date | | | |Both | |


## Institution QF-EHEA Level(institutions.models.InstitutionQFEHEALevel)

```

    List of QF-EHEA levels that are valid for each institution.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|institution |integer | | |True | |FK:institutions.models.Institution |
|qf_ehea_level |integer | | |True | |FK:lists.models.QFEHEALevel |
|qf_ehea_level_source |varchar(20) | | | | | |
|qf_ehea_level_source_note |text | | | |Blank | |
|qf_ehea_level_valid_from |date | | | | | |
|qf_ehea_level_valid_to |date | | | |Both | |
|qf_ehea_level_verified |boolean | | | |Blank | |


## ETER Record(institutions.models.InstitutionETERRecord)

```

    Periodically updated list of institutions managed by ETER.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|eter_id |varchar(15) | | | | | |
|national_identifier |varchar(20) | | | | | |
|name |varchar(200) | | | | | |
|name_english |varchar(200) | | | |Blank | |
|acronym |varchar(30) | | | |Blank | |
|country |varchar(3) | | | | | |
|city |varchar(100) | | | |Blank | |
|lat |double precision | | | |Both | |
|long |double precision | | | |Both | |
|website |varchar(200) | | | | | |
|ISCED_lowest |varchar(10) | | | | | |
|ISCED_highest |varchar(10) | | | | | |
|valid_from_year |date | | | | | |
|data_updated |date | | | | | |
|eter_link |varchar(200) | | | |Blank | |


## Institution Historical Relationship Type(institutions.models.InstitutionHistoricalRelationshipType)

```

    Historical relationship types between institutions
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|type_from |varchar(200) | | | | | |
|type_to |varchar(200) | | | | | |


## Institution Historical Relationship(institutions.models.InstitutionHistoricalRelationship)

```

    Historical relationships between institutions
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|institution_source |integer | | |True | |FK:institutions.models.Institution |
|institution_target |integer | | |True | |FK:institutions.models.Institution |
|relationship_type |integer | | |True | |FK:institutions.models.InstitutionHistoricalRelationshipType |
|relationship_note |varchar(300) | | | |Both | |
|relationship_date |date | | | | | |


## Institution Hierarchical Relationship(institutions.models.InstitutionHierarchicalRelationship)

```

    Hierarchival relationships between institutions
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|institution_parent |integer | | |True | |FK:institutions.models.Institution |
|institution_child |integer | | |True | |FK:institutions.models.Institution |
|relationship_note |varchar(300) | | | |Both | |
|valid_from |date | | | |Both | |
|valid_to |date | | | |Both | |


## Institution Historical Field(institutions.models.InstitutionHistoricalField)

```

    Name of the db_fields which can contain historical data of the institution.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|field |varchar(50) | | | | | |


## Institution Flag(institutions.models.InstitutionFlag)

```

    Flags belonging to an institution
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|institution |integer | | |True | |FK:institutions.models.Institution |
|flag |integer | | |True | |FK:lists.models.Flag |
|flag_message |text | | | |Blank | |
|active |boolean | | | |Blank | |
|removed_by_eqar |boolean | | | |Blank | |
|created_at |timestamp with time zone | | | |Blank | |
|updated_at |timestamp with time zone | | | |Blank | |

Options
```
unique_together : (('institution', 'flag_message'),)
```


## Institution Historical Data(institutions.models.InstitutionHistoricalData)

```

    The historical data that institutions change.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|institution |integer | | |True | |FK:institutions.models.Institution |
|field |integer | | |True | |FK:institutions.models.InstitutionHistoricalField |
|record_id |integer | | | |Both | |
|value |varchar(200) | | | | | |
|valid_from |date | | | |Both | |
|valid_to |date | | | |Both | |


## Institution Update Log(institutions.models.InstitutionUpdateLog)

```

    Updates happened with a report
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|institution |integer | | |True | |FK:institutions.models.Institution |
|note |text | | | |Both | |
|updated_at |timestamp with time zone | | | |Blank | |
|updated_by |integer | | |True |Both |FK:django.contrib.auth.models.User |


## Language(lists.models.Language)

```
Language(id, iso_639_1, iso_639_2, language_name_en)
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|iso_639_1 |varchar(10) | | | | | |
|iso_639_2 |varchar(10) | | | |Blank | |
|language_name_en |varchar(100) | |True | | | |


## QF-EHEA level(lists.models.QFEHEALevel)

```
QFEHEALevel(id, code, level)
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|code |integer | | | |Both | |
|level |varchar(20) | | | | | |


## Association(lists.models.Association)

```
Association(id, association)
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|association |varchar(200) | | | | | |


## EQAR Decision Type(lists.models.EQARDecisionType)

```
EQARDecisionType(id, type)
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|type |varchar(25) | | | | | |


## Identifier Resource(lists.models.IdentifierResource)

```
IdentifierResource(id, resource)
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|resource |varchar(50) | | | | | |


## Permission Type(lists.models.PermissionType)

```
PermissionType(id, type)
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|type |varchar(50) | | | | | |


## Flag(lists.models.Flag)

```
Flag(id, flag)
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|flag |varchar(20) | | | | | |


## programme-country relationship(programmes.models.Programme_countries)

```
Programme_countries(id, programme, country)
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|programme |integer | | |True | |FK:programmes.models.Programme |
|country |integer | | |True | |FK:countries.models.Country |

Options
```
unique_together : (('programme', 'country'),)
```


## Programmme(programmes.models.Programme)

```

    Institutional programmes or joint-programmes evaluated in reports.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|report |integer | | |True | |FK:reports.models.Report |
|name_primary |varchar(255) | | | |Blank | |
|nqf_level |varchar(255) | | | |Blank | |
|qf_ehea_level |integer | | |True |Both |FK:lists.models.QFEHEALevel |
|countries | | | | |Blank |M2M:countries.models.Country (through: programmes.models.Programme_countries) |


## Programme Name(programmes.models.ProgrammeName)

```

    One or more names of institutional programmes.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|programme |integer | | |True | |FK:programmes.models.Programme |
|name |varchar(255) | | | |Blank | |
|name_is_primary |boolean | | | |Blank | |
|qualification |varchar(255) | | | |Blank | |

Options
```
unique_together : (('programme', 'name'),)
```


## Programme Identifier(programmes.models.ProgrammeIdentifier)

```

    List of identifiers for the programme and the source of the identifier.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|programme |integer | | |True | |FK:programmes.models.Programme |
|identifier |varchar(50) | | | | | |
|agency |integer | | |True | |FK:agencies.models.Agency |
|resource |varchar(200) | | | |Blank | |

Options
```
unique_together : (('programme', 'agency', 'resource'),)
```


## report-institution relationship(reports.models.Report_institutions)

```
Report_institutions(id, report, institution)
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|report |integer | | |True | |FK:reports.models.Report |
|institution |integer | | |True | |FK:institutions.models.Institution |

Options
```
unique_together : (('report', 'institution'),)
```


## Report(reports.models.Report)

```

    List of reports and evaluations produced on HE institutions by EQAR registered agencies.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|agency |integer | | |True | |FK:agencies.models.Agency |
|local_identifier |varchar(255) | | | |Both | |
|agency_esg_activity |integer | | |True | |FK:agencies.models.AgencyESGActivity |
|name |varchar(300) | | | | | |
|status |integer | | |True | |FK:reports.models.ReportStatus |
|decision |integer | | |True | |FK:reports.models.ReportDecision |
|valid_from |date | | | | | |
|valid_to |date | | | |Both | |
|flag |integer | | |True | |FK:lists.models.Flag |
|flag_log |text | | | |Blank | |
|other_comment |text | | | |Blank | |
|internal_note |text | | | |Blank | |
|created_at |timestamp with time zone | | | |Blank | |
|created_by |integer | | |True |Both |FK:django.contrib.auth.models.User |
|updated_at |timestamp with time zone | | | | | |
|updated_by |integer | | |True |Both |FK:django.contrib.auth.models.User |
|institutions | | | | | |M2M:institutions.models.Institution (through: reports.models.Report_institutions) |

Options
```
unique_together : (('agency', 'local_identifier'),)
```


## Report Status(reports.models.ReportStatus)

```

    Status of the reports.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|status |varchar(50) | | | | | |


## Report Decision(reports.models.ReportDecision)

```

    Decision described in the report.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|decision |varchar(50) | | | | | |


## Report Link(reports.models.ReportLink)

```

    Links to records on individual reports and evaluations at agency’s site.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|report |integer | | |True | |FK:reports.models.Report |
|link_display_name |varchar(200) | | | |Both | |
|link |varchar(255) | | | |Both | |


## reportfile-language relationship(reports.models.ReportFile_languages)

```
ReportFile_languages(id, reportfile, language)
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|reportfile |integer | | |True | |FK:reports.models.ReportFile |
|language |integer | | |True | |FK:lists.models.Language |

Options
```
unique_together : (('reportfile', 'language'),)
```


## Report File(reports.models.ReportFile)

```

    PDF versions of reports and evaluations.
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|report |integer | | |True | |FK:reports.models.Report |
|file_display_name |varchar(255) | | | |Blank | |
|file_original_location |varchar(500) | | | |Blank | |
|file |varchar(255) | | | |Blank | |
|languages | | | | | |M2M:lists.models.Language (through: reports.models.ReportFile_languages) |


## Report Flag(reports.models.ReportFlag)

```

    Flags belonging to a report
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|report |integer | | |True | |FK:reports.models.Report |
|flag |integer | | |True | |FK:lists.models.Flag |
|flag_message |text | | | |Blank | |
|active |boolean | | | |Blank | |
|removed_by_eqar |boolean | | | |Blank | |
|created_at |timestamp with time zone | | | |Blank | |
|updated_at |timestamp with time zone | | | |Blank | |

Options
```
unique_together : (('report', 'flag_message'),)
```


## Report Update Log(reports.models.ReportUpdateLog)

```

    Updates happened with a report
    
```

|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|
|id |serial |True |True | |Blank | |
|report |integer | | |True | |FK:reports.models.Report |
|note |text | | | |Both | |
|updated_at |timestamp with time zone | | | |Blank | |
|updated_by |integer | | |True |Both |FK:django.contrib.auth.models.User |



