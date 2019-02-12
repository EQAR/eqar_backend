



## Agency(agencies.models.Agency)

```

    List of registered EQAR agencies.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|deqar id |deqar_id |integer | | | | | |
|name primary |name_primary |varchar(200) | | | |Blank | |
|acronym primary |acronym_primary |varchar(20) | | | |Blank | |
|contact person |contact_person |varchar(150) | | | | | |
|fax |fax |varchar(20) | | | |Blank | |
|address |address |text | | | | | |
|country |country |integer | | |True | |FK:countries.models.Country |
|website link |website_link |varchar(100) | | | | | |
|logo |logo |varchar(100) | | | |Both | |
|geographical focus |geographical_focus |integer | | |True |Both |FK:agencies.models.AgencyGeographicalFocus |
|specialisation note |specialisation_note |text | | | |Blank | |
|reports link |reports_link |varchar(200) | | | |Both | |
|description note |description_note |text | | | | | |
|is registered |is_registered |boolean | | | | | |
|registration start |registration_start |date | | | | | |
|registration valid to |registration_valid_to |date | | | | | |
|registration note |registration_note |text | | | |Blank | |
|flag |flag |integer | | |True | |FK:lists.models.Flag |
|flag log |flag_log |text | | | |Blank | |
|related agencies |related_agencies | | | | | |M2M:agencies.models.Agency (through: agencies.models.AgencyRelationship) |


## agency geographical focus(agencies.models.AgencyGeographicalFocus)

```

    List of the agency focus level.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|focus |focus |varchar(20) | |True | | | |


## Agency Name(agencies.models.AgencyName)

```

    List of agency names/acronyms in a particular period.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|name note |name_note |text | | | |Blank | |
|name valid to |name_valid_to |date | | | |Both | |


## agency name version(agencies.models.AgencyNameVersion)

```

    Different versions of agency names with transliteration as applicable.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|agency name |agency_name |integer | | |True | |FK:agencies.models.AgencyName |
|name |name |varchar(200) | | | | | |
|name transliterated |name_transliterated |varchar(200) | | | |Blank | |
|name is primary |name_is_primary |boolean | | | | | |
|acronym |acronym |varchar(20) | | | |Blank | |
|acronym transliterated |acronym_transliterated |varchar(20) | | | |Blank | |
|acronym is primary |acronym_is_primary |boolean | | | | | |


## agency phone(agencies.models.AgencyPhone)

```

    One or more phone numbers for each agency.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|phone |phone |varchar(20) | | | | | |

Options
```
unique_together : (('agency', 'phone'),)
```


## agency email(agencies.models.AgencyEmail)

```

    One or more contact emails for each agency.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|email |email |varchar(50) | | | | | |

Options
```
unique_together : (('agency', 'email'),)
```


## agency focus country(agencies.models.AgencyFocusCountry)

```

    List of EHEA countries where the agency has evaluated,
    accredited or audited higher education institutions or programmes.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|country |country |integer | | |True | |FK:countries.models.Country |
|country is official |country_is_official |boolean | | | | | |
|country is crossborder |country_is_crossborder |boolean | | | | | |
|country valid from |country_valid_from |date | | | | | |
|country valid to |country_valid_to |date | | | |Both | |

Options
```
unique_together : (('agency', 'country'),)
```


## agency esg activity(agencies.models.AgencyESGActivity)

```

    External quality assurance activities in the scope of the ESG.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|activity |activity |varchar(500) | | | | | |
|activity display |activity_display |varchar(500) | | | |Both | |
|activity local identifier |activity_local_identifier |varchar(100) | | | |Blank | |
|activity description |activity_description |varchar(300) | | | |Blank | |
|activity type |activity_type |integer | | |True | |FK:agencies.models.AgencyActivityType |
|reports link |reports_link |varchar(200) | | | |Both | |
|activity valid from |activity_valid_from |date | | | | | |
|activity valid to |activity_valid_to |date | | | |Both | |


## agency activity type(agencies.models.AgencyActivityType)

```

    Agency activity types.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|type |type |varchar(30) | |True | | | |


## agency relationship(agencies.models.AgencyRelationship)

```

    Mergers, spin offs and other historical events which link two agencies.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|from agency |from_agency |integer | | |True | |FK:agencies.models.Agency |
|to agency |to_agency |integer | | |True | |FK:agencies.models.Agency |
|note |note |text | | | | | |
|date |date |date | | | | | |

Options
```
unique_together : (('from_agency', 'to_agency'),)
```


## agency membership(agencies.models.AgencyMembership)

```

    List of associations to which each agency belongs.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|association |association |integer | | |True | |FK:lists.models.Association |
|membership valid from |membership_valid_from |date | | | | | |
|membership valid to |membership_valid_to |date | | | |Both | |

Options
```
unique_together : (('agency', 'association'),)
```


## agency eqar decision(agencies.models.AgencyEQARDecision)

```

    List of EQAR register decision dates for each agency with any connected reports.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|decision date |decision_date |date | | | | | |
|decision type |decision_type |integer | | |True | |FK:lists.models.EQARDecisionType |
|decision file |decision_file |varchar(100) | | | | | |
|decision file extra |decision_file_extra |varchar(100) | | | |Blank | |


## Submitting Agency(agencies.models.SubmittingAgency)

```

    List of agencies registered to submit data to DEQAR.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|agency |agency |integer | | |True |Both |FK:agencies.models.Agency |
|external agency |external_agency |varchar(200) | | | |Blank | |
|external agency acronym |external_agency_acronym |varchar(20) | | | |Blank | |
|registration from |registration_from |date | | | | | |
|registration to |registration_to |date | | | |Both | |


## agency proxy(agencies.models.AgencyProxy)

```

    List of EQAR registered agencies whose data is submitted to DEQAR by a different submitting agency.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|submitting agency |submitting_agency |integer | | |True | |FK:agencies.models.SubmittingAgency |
|allowed agency |allowed_agency |integer | | |True | |FK:agencies.models.Agency |
|proxy from |proxy_from |date | | | | | |
|proxy to |proxy_to |date | | | |Both | |

Options
```
unique_together : (('submitting_agency', 'allowed_agency'),)
```


## agency historical field(agencies.models.AgencyHistoricalField)

```

    Name of the db_fields which can contain historical data.
    This will save changed data from named fields.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|field |field |varchar(50) | | | | | |


## agency historical data(agencies.models.AgencyHistoricalData)

```

    The historical data that agencies change.
    Either valid from or valid to date must be filled.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|field |field |integer | | |True | |FK:agencies.models.AgencyHistoricalField |
|record id |record_id |integer | | | |Both | |
|value |value |varchar(200) | | | | | |
|valid from |valid_from |date | | | |Both | |
|valid to |valid_to |date | | | |Both | |


## Country(countries.models.Country)

```

    Countries related to HE institutions, EQAR agencies and other QA activities.
    Includes information on QA requirements imposed in the country.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|iso 3166 alpha2 |iso_3166_alpha2 |varchar(2) | | | | | |
|iso 3166 alpha3 |iso_3166_alpha3 |varchar(3) | | | | | |
|name english |name_english |varchar(100) | |True | | | |
|ehea is member |ehea_is_member |boolean | | | | | |
|eqar governmental member start |eqar_governmental_member_start |date | | | |Both | |
|qa requirement note |qa_requirement_note |text | | | |Blank | |
|external QAA is permitted |external_QAA_is_permitted |integer | | |True | |FK:lists.models.PermissionType |
|external QAA note |external_QAA_note |text | | | |Both | |
|eligibility |eligibility |text | | | |Both | |
|conditions |conditions |text | | | |Both | |
|recognition |recognition |text | | | |Both | |
|european approach is permitted |european_approach_is_permitted |integer | | |True | |FK:lists.models.PermissionType |
|european approach note |european_approach_note |text | | | |Both | |
|general note |general_note |text | | | |Blank | |
|flag |flag |integer | | |True | |FK:lists.models.Flag |
|flag log |flag_log |text | | | |Blank | |


## country qa requirement(countries.models.CountryQARequirement)

```
CountryQARequirement(id, country, qa_requirement, qa_requirement_type, qa_requirement_note, requirement_valid_from, requirement_valid_to)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|country |country |integer | | |True | |FK:countries.models.Country |
|qa requirement |qa_requirement |varchar(200) | | | | | |
|qa requirement type |qa_requirement_type |integer | | |True | |FK:countries.models.CountryQARequirementType |
|qa requirement note |qa_requirement_note |text | | | |Blank | |
|requirement valid from |requirement_valid_from |date | | | | | |
|requirement valid to |requirement_valid_to |date | | | |Both | |


## country qa requirement type(countries.models.CountryQARequirementType)

```

    Type of country requriement types.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|qa requirement type |qa_requirement_type |varchar(200) | | | |Blank | |


## country qaa regulation(countries.models.CountryQAARegulation)

```

    List of QAA regulations imposed on external agencies by individual countries.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|country |country |integer | | |True | |FK:countries.models.Country |
|regulation |regulation |varchar(200) | | | |Blank | |
|regulation url |regulation_url |varchar(200) | | | |Blank | |
|regulation valid from |regulation_valid_from |date | | | | | |
|regulation valid to |regulation_valid_to |date | | | |Both | |


## country historical field(countries.models.CountryHistoricalField)

```

    Name of the db_fields which can contain historical data of the country.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|field |field |varchar(50) | | | | | |


## country historical data(countries.models.CountryHistoricalData)

```

    The historical data that country change.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|country |country |integer | | |True | |FK:countries.models.Country |
|field |field |integer | | |True | |FK:countries.models.CountryHistoricalField |
|record id |record_id |integer | | | |Both | |
|value |value |varchar(200) | | | | | |
|valid from |valid_from |date | | | |Both | |
|valid to |valid_to |date | | | |Both | |


## institution(institutions.models.Institution)

```

    List of institutions reviewed or evaluated by EQAR registered agencies.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|deqar id |deqar_id |varchar(25) | | | |Blank | |
|eter |eter |integer | | |True |Both |FK:institutions.models.InstitutionETERRecord |
|name primary |name_primary |varchar(200) | | | |Blank | |
|website link |website_link |varchar(150) | | | | | |
|founding date |founding_date |date | | | |Both | |
|closure date |closure_date |date | | | |Both | |
|national identifier |national_identifier |varchar(50) | | | |Both | |
|source note |source_note |text | | | |Blank | |
|flag |flag |integer | | |True | |FK:lists.models.Flag |
|flag log |flag_log |text | | | |Blank | |
|name sort |name_sort |varchar(500) | | | |Blank | |
|has report |has_report |boolean | | | | | |


## institution identifier(institutions.models.InstitutionIdentifier)

```

    List of other (non-ETER) identifiers for the institution and the source of the identifier.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|identifier |identifier |varchar(50) | | | | | |
|agency |agency |integer | | |True |Both |FK:agencies.models.Agency |
|resource |resource |varchar(200) | | | |Blank | |
|identifier valid from |identifier_valid_from |date | | | | | |
|identifier valid to |identifier_valid_to |date | | | |Both | |

Options
```
unique_together : (('institution', 'agency', 'resource'),)
```


## Institution Name(institutions.models.InstitutionName)

```

    List of names/acronym used for an institution in a particular period.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|name official |name_official |varchar(200) | | | | | |
|name official transliterated |name_official_transliterated |varchar(200) | | | |Blank | |
|name english |name_english |varchar(200) | | | |Blank | |
|acronym |acronym |varchar(30) | | | |Blank | |
|name source note |name_source_note |text | | | |Blank | |
|name valid to |name_valid_to |date | | | |Both | |


## institution name version(institutions.models.InstitutionNameVersion)

```

    Different versions of institution names with transliteration as applicable.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|institution name |institution_name |integer | | |True | |FK:institutions.models.InstitutionName |
|name |name |varchar(200) | | | | | |
|transliteration |transliteration |varchar(200) | | | |Blank | |
|name version source |name_version_source |varchar(20) | | | |Blank | |
|name version source note |name_version_source_note |text | | | |Blank | |


## institution country(institutions.models.InstitutionCountry)

```

    List of countries where the institution is located.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|country |country |integer | | |True | |FK:countries.models.Country |
|city |city |varchar(100) | | | |Both | |
|lat |lat |double precision | | | |Both | |
|long |long |double precision | | | |Both | |
|country source |country_source |varchar(20) | | | | | |
|country source note |country_source_note |text | | | |Blank | |
|country valid from |country_valid_from |date | | | | | |
|country valid to |country_valid_to |date | | | |Both | |
|country verified |country_verified |boolean | | | | | |


## institution nqf level(institutions.models.InstitutionNQFLevel)

```

    List of NQF levels that are valid for each institution.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|nqf level |nqf_level |varchar(10) | | | | | |
|nqf level source |nqf_level_source |varchar(20) | | | | | |
|nqf level source note |nqf_level_source_note |text | | | |Blank | |
|nqf level valid from |nqf_level_valid_from |date | | | | | |
|nqf level valid to |nqf_level_valid_to |date | | | |Both | |


## institution qfehea level(institutions.models.InstitutionQFEHEALevel)

```

    List of QF-EHEA levels that are valid for each institution.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|qf ehea level |qf_ehea_level |integer | | |True | |FK:lists.models.QFEHEALevel |
|qf ehea level source |qf_ehea_level_source |varchar(20) | | | | | |
|qf ehea level source note |qf_ehea_level_source_note |text | | | |Blank | |
|qf ehea level valid from |qf_ehea_level_valid_from |date | | | | | |
|qf ehea level valid to |qf_ehea_level_valid_to |date | | | |Both | |
|qf ehea level verified |qf_ehea_level_verified |boolean | | | | | |


## ETER Record(institutions.models.InstitutionETERRecord)

```

    Periodically updated list of institutions managed by ETER.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|eter id |eter_id |varchar(15) | | | | | |
|national identifier |national_identifier |varchar(20) | | | | | |
|name |name |varchar(200) | | | | | |
|name english |name_english |varchar(200) | | | |Blank | |
|acronym |acronym |varchar(30) | | | |Blank | |
|country |country |varchar(3) | | | | | |
|city |city |varchar(100) | | | |Blank | |
|lat |lat |double precision | | | |Both | |
|long |long |double precision | | | |Both | |
|website |website |varchar(200) | | | | | |
|ISCED lowest |ISCED_lowest |varchar(10) | | | | | |
|ISCED highest |ISCED_highest |varchar(10) | | | | | |
|valid from year |valid_from_year |date | | | | | |
|data updated |data_updated |date | | | | | |
|eter link |eter_link |varchar(200) | | | |Blank | |


## Institution Historical Relationship Type(institutions.models.InstitutionHistoricalRelationshipType)

```

    Historical relationship types between institutions
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|type from |type_from |varchar(200) | | | | | |
|type to |type_to |varchar(200) | | | | | |


## Institution Historical Relationship(institutions.models.InstitutionHistoricalRelationship)

```

    Historical relationships between institutions
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|institution source |institution_source |integer | | |True | |FK:institutions.models.Institution |
|institution target |institution_target |integer | | |True | |FK:institutions.models.Institution |
|relationship type |relationship_type |integer | | |True | |FK:institutions.models.InstitutionHistoricalRelationshipType |
|relationship note |relationship_note |varchar(300) | | | |Both | |
|relationship date |relationship_date |date | | | | | |


## Institution Hierarchical Relationship(institutions.models.InstitutionHierarchicalRelationship)

```

    Hierarchival relationships between institutions
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|institution parent |institution_parent |integer | | |True | |FK:institutions.models.Institution |
|institution child |institution_child |integer | | |True | |FK:institutions.models.Institution |
|relationship note |relationship_note |varchar(300) | | | |Both | |
|valid from |valid_from |date | | | |Both | |
|valid to |valid_to |date | | | |Both | |


## institution historical field(institutions.models.InstitutionHistoricalField)

```

    Name of the db_fields which can contain historical data of the institution.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|field |field |varchar(50) | | | | | |


## institution historical data(institutions.models.InstitutionHistoricalData)

```

    The historical data that institutions change.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|field |field |integer | | |True | |FK:institutions.models.InstitutionHistoricalField |
|record id |record_id |integer | | | |Both | |
|value |value |varchar(200) | | | | | |
|valid from |valid_from |date | | | |Both | |
|valid to |valid_to |date | | | |Both | |


## language(lists.models.Language)

```
Language(id, iso_639_1, iso_639_2, language_name_en)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|iso 639 1 |iso_639_1 |varchar(10) | | | | | |
|iso 639 2 |iso_639_2 |varchar(10) | | | |Blank | |
|language name en |language_name_en |varchar(100) | |True | | | |


## QF-EHEA level(lists.models.QFEHEALevel)

```
QFEHEALevel(id, code, level)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|code |code |integer | | | |Both | |
|level |level |varchar(20) | | | | | |


## association(lists.models.Association)

```
Association(id, association)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|association |association |varchar(200) | | | | | |


## EQAR Decision Type(lists.models.EQARDecisionType)

```
EQARDecisionType(id, type)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|type |type |varchar(25) | | | | | |


## Identifier Resource(lists.models.IdentifierResource)

```
IdentifierResource(id, resource)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|resource |resource |varchar(50) | | | | | |


## Permission Type(lists.models.PermissionType)

```
PermissionType(id, type)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|type |type |varchar(50) | | | | | |


## Flag(lists.models.Flag)

```
Flag(id, flag)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|flag |flag |varchar(20) | | | | | |


## programme-country relationship(programmes.models.Programme_countries)

```
Programme_countries(id, programme, country)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|programme |programme |integer | | |True | |FK:programmes.models.Programme |
|country |country |integer | | |True | |FK:countries.models.Country |

Options
```
unique_together : (('programme', 'country'),)
```


## programme(programmes.models.Programme)

```

    Institutional programmes or joint-programmes evaluated in reports.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|name primary |name_primary |varchar(255) | | | |Blank | |
|nqf level |nqf_level |varchar(255) | | | |Blank | |
|qf ehea level |qf_ehea_level |integer | | |True |Both |FK:lists.models.QFEHEALevel |
|countries |countries | | | | |Blank |M2M:countries.models.Country (through: programmes.models.Programme_countries) |


## programme name(programmes.models.ProgrammeName)

```

    One or more names of institutional programmes.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|programme |programme |integer | | |True | |FK:programmes.models.Programme |
|name |name |varchar(255) | | | |Blank | |
|name is primary |name_is_primary |boolean | | | | | |
|qualification |qualification |varchar(255) | | | |Blank | |

Options
```
unique_together : (('programme', 'name'),)
```


## programme identifier(programmes.models.ProgrammeIdentifier)

```

    List of identifiers for the programme and the source of the identifier.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|programme |programme |integer | | |True | |FK:programmes.models.Programme |
|identifier |identifier |varchar(50) | | | | | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|resource |resource |varchar(200) | | | |Blank | |

Options
```
unique_together : (('programme', 'agency', 'resource'),)
```


## report-institution relationship(reports.models.Report_institutions)

```
Report_institutions(id, report, institution)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |

Options
```
unique_together : (('report', 'institution'),)
```


## report(reports.models.Report)

```

    List of reports and evaluations produced on HE institutions by EQAR registered agencies.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|local identifier |local_identifier |varchar(255) | | | |Both | |
|agency esg activity |agency_esg_activity |integer | | |True | |FK:agencies.models.AgencyESGActivity |
|name |name |varchar(300) | | | | | |
|status |status |integer | | |True | |FK:reports.models.ReportStatus |
|decision |decision |integer | | |True | |FK:reports.models.ReportDecision |
|valid from |valid_from |date | | | | | |
|valid to |valid_to |date | | | |Both | |
|flag |flag |integer | | |True | |FK:lists.models.Flag |
|flag log |flag_log |text | | | |Blank | |
|institutions |institutions | | | | | |M2M:institutions.models.Institution (through: reports.models.Report_institutions) |

Options
```
unique_together : (('agency', 'local_identifier'),)
```


## report status(reports.models.ReportStatus)

```

    Status of the reports.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|status |status |varchar(50) | | | | | |


## report decision(reports.models.ReportDecision)

```

    Decision described in the report.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|decision |decision |varchar(50) | | | | | |


## report link(reports.models.ReportLink)

```

    Links to records on individual reports and evaluations at agency’s site.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|link display name |link_display_name |varchar(200) | | | |Both | |
|link |link |varchar(255) | | | |Both | |


## reportfile-language relationship(reports.models.ReportFile_languages)

```
ReportFile_languages(id, reportfile, language)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|reportfile |reportfile |integer | | |True | |FK:reports.models.ReportFile |
|language |language |integer | | |True | |FK:lists.models.Language |

Options
```
unique_together : (('reportfile', 'language'),)
```


## report file(reports.models.ReportFile)

```

    PDF versions of reports and evaluations.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |serial |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|file display name |file_display_name |varchar(255) | | | |Blank | |
|file original location |file_original_location |varchar(500) | | | |Blank | |
|file |file |varchar(255) | | | |Blank | |
|languages |languages | | | | | |M2M:lists.models.Language (through: reports.models.ReportFile_languages) |



