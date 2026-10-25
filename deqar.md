



## Agency(agencies.models.Agency)

```

    List of registered EQAR agencies.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
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
|registration start |registration_start |date | | | |Both | |
|registration valid to |registration_valid_to |date | | | |Both | |
|registration note |registration_note |text | | | |Blank | |
|flag |flag |integer | | |True | |FK:lists.models.Flag |
|flag log |flag_log |text | | | |Blank | |
|internal note |internal_note |text | | | |Both | |
|created at |created_at |timestamp with time zone | | | |Blank | |
|created by |created_by |integer | | |True |Both |FK:django.contrib.auth.models.User |
|related agencies |related_agencies | | | | | |M2M:agencies.models.Agency (through: agencies.models.AgencyRelationship) |

Options
```
ordering : ('acronym_primary', 'name_primary')
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Geographical Focus(agencies.models.AgencyGeographicalFocus)

```

    List of the agency focus level.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|focus |focus |varchar(20) | |True | | | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Name(agencies.models.AgencyName)

```

    List of agency names/acronyms in a particular period.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|name note |name_note |text | | | |Blank | |
|name valid to |name_valid_to |date | | | |Both | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Name Version(agencies.models.AgencyNameVersion)

```

    Different versions of agency names with transliteration as applicable.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency name |agency_name |integer | | |True | |FK:agencies.models.AgencyName |
|name |name |varchar(200) | | | | | |
|name transliterated |name_transliterated |varchar(200) | | | |Blank | |
|name is primary |name_is_primary |boolean | | | | | |
|acronym |acronym |varchar(20) | | | |Blank | |
|acronym transliterated |acronym_transliterated |varchar(20) | | | |Blank | |
|acronym is primary |acronym_is_primary |boolean | | | | | |

Options
```
ordering : ('-name_is_primary', 'name')
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Phone(agencies.models.AgencyPhone)

```

    One or more phone numbers for each agency.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|phone |phone |varchar(20) | | | | | |

Options
```
unique_together : (('agency', 'phone'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Email(agencies.models.AgencyEmail)

```

    One or more contact emails for each agency.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|email |email |varchar(50) | | | | | |

Options
```
unique_together : (('agency', 'email'),)
ordering : ('email',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Focus Country(agencies.models.AgencyFocusCountry)

```

    List of EHEA countries where the agency has evaluated,
    accredited or audited higher education institutions or programmes.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|country |country |integer | | |True | |FK:countries.models.Country |
|country is official |country_is_official |boolean | | | | | |
|country is crossborder |country_is_crossborder |boolean | | | | | |
|country valid from |country_valid_from |date | | | | | |
|country valid to |country_valid_to |date | | | |Both | |

Options
```
unique_together : (('agency', 'country'),)
ordering : ('country__name_english',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## ESG Activity(agencies.models.AgencyESGActivity)

```

    External quality assurance activities in the scope of the ESG.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|activity |activity |varchar(500) | | | |Both | |
|activity group |activity_group |integer | | |True | |FK:agencies.models.AgencyActivityGroup |
|activity display |activity_display |varchar(500) | | | |Both | |
|activity local identifier |activity_local_identifier |varchar(100) | | | |Blank | |
|activity description |activity_description |varchar(300) | | | |Blank | |
|reports link |reports_link |varchar(200) | | | |Both | |
|activity valid from |activity_valid_from |date | | | | | |
|activity valid to |activity_valid_to |date | | | |Both | |

Options
```
ordering : ('agency', 'activity')
default_permissions : ('add', 'change', 'delete', 'view')
```


## ESG Activity Group(agencies.models.AgencyActivityGroup)

```

       External quality assurance activity groups.
       
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|activity |activity |varchar(500) | | | | | |
|activity type |activity_type |integer | | |True | |FK:agencies.models.AgencyActivityType |
|reports link |reports_link |varchar(200) | | | |Both | |

Options
```
ordering : ('activity', 'activity_type')
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Activity Type(agencies.models.AgencyActivityType)

```

    Agency activity types.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|type |type |varchar(30) | |True | | | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Relationship(agencies.models.AgencyRelationship)

```

    Mergers, spin offs and other historical events which link two agencies.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|from agency |from_agency |integer | | |True | |FK:agencies.models.Agency |
|to agency |to_agency |integer | | |True | |FK:agencies.models.Agency |
|note |note |text | | | | | |
|date |date |date | | | | | |

Options
```
unique_together : (('from_agency', 'to_agency'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Membership(agencies.models.AgencyMembership)

```

    List of associations to which each agency belongs.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|association |association |integer | | |True | |FK:lists.models.Association |
|membership valid from |membership_valid_from |date | | | | | |
|membership valid to |membership_valid_to |date | | | |Both | |

Options
```
unique_together : (('agency', 'association'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency EQAR Decision(agencies.models.AgencyEQARDecision)

```

    List of EQAR register decision dates for each agency with any connected reports.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|decision date |decision_date |date | | | | | |
|decision type |decision_type |integer | | |True | |FK:lists.models.EQARDecisionType |
|decision file |decision_file |varchar(100) | | | | | |
|decision file extra |decision_file_extra |varchar(100) | | | |Blank | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Submitting Agency(agencies.models.SubmittingAgency)

```

    List of agencies registered to submit data to DEQAR.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True |Both |FK:agencies.models.Agency |
|external agency |external_agency |varchar(200) | | | |Blank | |
|external agency acronym |external_agency_acronym |varchar(20) | | | |Blank | |
|registration from |registration_from |date | | | | | |
|registration to |registration_to |date | | | |Both | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Proxy(agencies.models.AgencyProxy)

```

    List of EQAR registered agencies whose data is submitted to DEQAR by a different submitting agency.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|submitting agency |submitting_agency |integer | | |True | |FK:agencies.models.SubmittingAgency |
|allowed agency |allowed_agency |integer | | |True | |FK:agencies.models.Agency |
|proxy from |proxy_from |date | | | | | |
|proxy to |proxy_to |date | | | |Both | |

Options
```
unique_together : (('submitting_agency', 'allowed_agency'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Historical Field(agencies.models.AgencyHistoricalField)

```

    Name of the db_fields which can contain historical data.
    This will save changed data from named fields.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|field |field |varchar(50) | | | | | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Historical Data(agencies.models.AgencyHistoricalData)

```

    The historical data that agencies change.
    Either valid from or valid to date must be filled.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|field |field |integer | | |True | |FK:agencies.models.AgencyHistoricalField |
|record id |record_id |integer | | | |Both | |
|value |value |varchar(200) | | | | | |
|valid from |valid_from |date | | | |Both | |
|valid to |valid_to |date | | | |Both | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Flag(agencies.models.AgencyFlag)

```

    Flags belonging to an agency
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|flag |flag |integer | | |True | |FK:lists.models.Flag |
|flag message |flag_message |text | | | |Blank | |
|active |active |boolean | | | | | |
|removed by eqar |removed_by_eqar |boolean | | | | | |
|created at |created_at |timestamp with time zone | | | |Blank | |
|updated at |updated_at |timestamp with time zone | | | |Blank | |

Options
```
unique_together : (('agency', 'flag_message'),)
ordering : ['id', 'flag__id']
default_permissions : ('add', 'change', 'delete', 'view')
```


## Agency Update Log(agencies.models.AgencyUpdateLog)

```

    Updates happened with an agency
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|note |note |text | | | |Both | |
|updated at |updated_at |timestamp with time zone | | | |Blank | |
|updated by |updated_by |integer | | |True |Both |FK:django.contrib.auth.models.User |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Country(countries.models.Country)

```

    Countries related to HE institutions, EQAR agencies and other QA activities.
    Includes information on QA requirements imposed in the country.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|parent |parent |integer | | |True |Both |FK:countries.models.Country |
|iso 3166 alpha2 |iso_3166_alpha2 |varchar(10) | |True | | | |
|iso 3166 alpha3 |iso_3166_alpha3 |varchar(3) | |True | |Both | |
|name english |name_english |varchar(100) | |True | | | |
|ehea is member |ehea_is_member |boolean | | | | | |
|eqar governmental member start |eqar_governmental_member_start |date | | | |Both | |
|qa requirement note |qa_requirement_note |text | | | |Blank | |
|external QAA is permitted |external_QAA_is_permitted |integer | | |True | |FK:lists.models.PermissionType |
|european approach is permitted |european_approach_is_permitted |integer | | |True | |FK:lists.models.PermissionType |
|general note |general_note |text | | | |Blank | |
|LRC signatory date |lrc_signatory_date |date | | | |Both | |
|QF-EHEA alignment date |qf_ehea_alignment_date |date | | | |Both | |
|EQF alignment date |eqf_alignment_date |date | | | |Both | |
|has full institution list |has_full_institution_list |boolean | | | | | |
|ehea key commitment |ehea_key_commitment |integer | | |True | |FK:lists.models.PermissionType |
|flag |flag |integer | | |True | |FK:lists.models.Flag |
|flag log |flag_log |text | | | |Blank | |
|internal note |internal_note |text | | | |Both | |
|orgreg subcountry label |orgreg_subcountry_label |varchar(200) | | | |Both | |
|orgreg eu 2 letter code |orgreg_eu_2_letter_code |varchar(3) | |True | |Both | |
|eu controlled vocab country |eu_controlled_vocab_country |varchar(250) | |True | |Both | |
|eu controlled vocab atu |eu_controlled_vocab_atu |varchar(250) | |True | |Both | |
|generic url |generic_url |varchar(250) | | | |Both | |
|created at |created_at |timestamp with time zone | | | |Blank | |
|created by |created_by |integer | | |True |Both |FK:django.contrib.auth.models.User |

Options
```
ordering : ('name_english',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## countryqarequirementgroup-countryinstitutiontype relationship(countries.models.CountryQARequirementGroup_institution_types)

```
CountryQARequirementGroup_institution_types(id, countryqarequirementgroup, countryinstitutiontype)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|countryqarequirementgroup |countryqarequirementgroup |integer | | |True | |FK:countries.models.CountryQARequirementGroup |
|countryinstitutiontype |countryinstitutiontype |integer | | |True | |FK:countries.models.CountryInstitutionType |

Options
```
unique_together : (('countryqarequirementgroup', 'countryinstitutiontype'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## countryqarequirementgroup-tneapprovaloutgoing relationship(countries.models.CountryQARequirementGroup_outgoing_tne_approval)

```
CountryQARequirementGroup_outgoing_tne_approval(id, countryqarequirementgroup, tneapprovaloutgoing)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|countryqarequirementgroup |countryqarequirementgroup |integer | | |True | |FK:countries.models.CountryQARequirementGroup |
|tneapprovaloutgoing |tneapprovaloutgoing |integer | | |True | |FK:lists.models.TneApprovalOutgoing |

Options
```
unique_together : (('countryqarequirementgroup', 'tneapprovaloutgoing'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## countryqarequirementgroup-mcqa relationship(countries.models.CountryQARequirementGroup_mc_qa)

```
CountryQARequirementGroup_mc_qa(id, countryqarequirementgroup, mcqa)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|countryqarequirementgroup |countryqarequirementgroup |integer | | |True | |FK:countries.models.CountryQARequirementGroup |
|mcqa |mcqa |integer | | |True | |FK:lists.models.McQa |

Options
```
unique_together : (('countryqarequirementgroup', 'mcqa'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Country QA Requirements Group(countries.models.CountryQARequirementGroup)

```

    One or more institution types of a country that share common QA requirements,
    including their possibilities for outgoing TNE and micro-credentials.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|country |country |integer | | |True | |FK:countries.models.Country |
|combination logic |combination_logic |varchar(3) | | | | |AND:cumulative (AND), OR:alternative (OR) |
|outgoing TNE possible |outgoing_tne_possible |integer | | |True |Both |FK:lists.models.TnePossible |
|outgoing TNE conditions |outgoing_tne_conditions |text | | | |Blank | |
|outgoing TNE QA regime |outgoing_tne_qa |integer | | |True |Both |FK:lists.models.TneQaOutgoing |
|MC possible |mc_possible |boolean | | | | | |
|MC credit limit |mc_credit_limit |smallint | | | |Both | |
|MC QA notes |mc_qa_note |text | | | |Blank | |
|institution types |institution_types | | | | |Blank |M2M:countries.models.CountryInstitutionType (through: countries.models.CountryQARequirementGroup_institution_types) |
|outgoing TNE approval needed |outgoing_tne_approval | | | | |Blank |M2M:lists.models.TneApprovalOutgoing (through: countries.models.CountryQARequirementGroup_outgoing_tne_approval) |
|MC QA regime |mc_qa | | | | |Blank |M2M:lists.models.McQa (through: countries.models.CountryQARequirementGroup_mc_qa) |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## countryqarequirement-qfehealevel relationship(countries.models.CountryQARequirement_qf_ehea_levels)

```
CountryQARequirement_qf_ehea_levels(id, countryqarequirement, qfehealevel)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|countryqarequirement |countryqarequirement |integer | | |True | |FK:countries.models.CountryQARequirement |
|qfehealevel |qfehealevel |integer | | |True | |FK:lists.models.QFEHEALevel |

Options
```
unique_together : (('countryqarequirement', 'qfehealevel'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## countryqarequirement-crossborderapproval relationship(countries.models.CountryQARequirement_cbqa_approval)

```
CountryQARequirement_cbqa_approval(id, countryqarequirement, crossborderapproval)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|countryqarequirement |countryqarequirement |integer | | |True | |FK:countries.models.CountryQARequirement |
|crossborderapproval |crossborderapproval |integer | | |True | |FK:lists.models.CrossBorderApproval |

Options
```
unique_together : (('countryqarequirement', 'crossborderapproval'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## countryqarequirement-crossborderrequirement relationship(countries.models.CountryQARequirement_cbqa_requirements)

```
CountryQARequirement_cbqa_requirements(id, countryqarequirement, crossborderrequirement)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|countryqarequirement |countryqarequirement |integer | | |True | |FK:countries.models.CountryQARequirement |
|crossborderrequirement |crossborderrequirement |integer | | |True | |FK:lists.models.CrossBorderRequirement |

Options
```
unique_together : (('countryqarequirement', 'crossborderrequirement'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Country QA Requirement(countries.models.CountryQARequirement)

```

    A specific QA requirement that applies to a group of institution types.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|group |group |integer | | |True | |FK:countries.models.CountryQARequirementGroup |
|ESG activity group |activity_group |integer | | |True |Both |FK:agencies.models.AgencyActivityGroup |
|duration |duration |smallint | | | |Both | |
|initial only |initial_only |boolean | | | | | |
|fields of education |fields_of_education |varchar(70)[] | | | |Blank | |
|full degrees |full_degrees |boolean | | | | | |
|micro credentials |micro_credentials |boolean | | | | | |
|notes |qa_requirement_note |text | | | |Blank | |
|valid from |requirement_valid_from |date | | | | | |
|valid to |requirement_valid_to |date | | | |Both | |
|CBQA possible |cbqa_possible |integer | | |True |Both |FK:lists.models.CrossBorderPossibility |
|CBQA other requirements note |cbqa_other_requirements_note |text | | | |Blank | |
|CBQA criteria |cbqa_criteria |integer | | |True |Both |FK:lists.models.CrossBorderCriteria |
|CBQA recognition |cbqa_recognition |integer | | |True |Both |FK:lists.models.CrossBorderDecision |
|EA possible |ea_possible |integer | | |True |Both |FK:lists.models.EuropeanApproachPossibility |
|EA note |ea_note |text | | | |Blank | |
|QF-EHEA levels |qf_ehea_levels | | | | |Blank |M2M:lists.models.QFEHEALevel (through: countries.models.CountryQARequirement_qf_ehea_levels) |
|CBQA approval needed |cbqa_approval | | | | |Blank |M2M:lists.models.CrossBorderApproval (through: countries.models.CountryQARequirement_cbqa_approval) |
|CBQA requirements |cbqa_requirements | | | | |Blank |M2M:lists.models.CrossBorderRequirement (through: countries.models.CountryQARequirement_cbqa_requirements) |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Country Institution Type(countries.models.CountryInstitutionType)

```

    National institutional categories of HE institutions in a country, aggregated from ETER (BAS.INSTCAT).
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|country |country |integer | | |True | |FK:countries.models.Country |
|name national |name_national |varchar(250) | | | | | |
|name english |name_english |varchar(250) | | | |Blank | |
|eter category standard |eter_category_standard |smallint | | | |Both |0:other, 1:university, 2:university of applied sciences |
|eter institution count |eter_institution_count |integer | | | | | |
|is active |is_active |boolean | | | | | |
|created at |created_at |timestamp with time zone | | | |Blank | |
|updated at |updated_at |timestamp with time zone | | | |Blank | |

Options
```
ordering : ('country', 'name_national')
default_permissions : ('add', 'change', 'delete', 'view')
```


## Country QAA Regulation(countries.models.CountryQAARegulation)

```

    Links to regulations relevant for QA in a country, either for the whole country or for a QA requirements group.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|country |country |integer | | |True | |FK:countries.models.Country |
|group |group |integer | | |True |Both |FK:countries.models.CountryQARequirementGroup |
|regulation |regulation |varchar(500) | | | |Blank | |
|regulation url |regulation_url |varchar(500) | | | |Blank | |
|regulation valid from |regulation_valid_from |date | | | | | |
|regulation valid to |regulation_valid_to |date | | | |Both | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## countryincomingtneregulation-tneorigingroup relationship(countries.models.CountryIncomingTneRegulation_origin_groups)

```
CountryIncomingTneRegulation_origin_groups(id, countryincomingtneregulation, tneorigingroup)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|countryincomingtneregulation |countryincomingtneregulation |integer | | |True | |FK:countries.models.CountryIncomingTneRegulation |
|tneorigingroup |tneorigingroup |integer | | |True | |FK:lists.models.TneOriginGroup |

Options
```
unique_together : (('countryincomingtneregulation', 'tneorigingroup'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## countryincomingtneregulation-tneapprovalincoming relationship(countries.models.CountryIncomingTneRegulation_incoming_tne_approval)

```
CountryIncomingTneRegulation_incoming_tne_approval(id, countryincomingtneregulation, tneapprovalincoming)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|countryincomingtneregulation |countryincomingtneregulation |integer | | |True | |FK:countries.models.CountryIncomingTneRegulation |
|tneapprovalincoming |tneapprovalincoming |integer | | |True | |FK:lists.models.TneApprovalIncoming |

Options
```
unique_together : (('countryincomingtneregulation', 'tneapprovalincoming'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Country Incoming TNE Regulation(countries.models.CountryIncomingTneRegulation)

```

    Rules for incoming transnational education (TNE), depending on the country of origin of the foreign HEI.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|country |country |integer | | |True | |FK:countries.models.Country |
|incoming TNE possible |incoming_tne_possible |integer | | |True | |FK:lists.models.TnePossible |
|incoming TNE conditions |incoming_tne_conditions |text | | | |Blank | |
|incoming TNE QA regime |incoming_tne_qa |integer | | |True | |FK:lists.models.TneQaIncoming |
|origin country groups |origin_groups | | | | |Blank |M2M:lists.models.TneOriginGroup (through: countries.models.CountryIncomingTneRegulation_origin_groups) |
|incoming TNE approval needed |incoming_tne_approval | | | | |Blank |M2M:lists.models.TneApprovalIncoming (through: countries.models.CountryIncomingTneRegulation_incoming_tne_approval) |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Country Update Log(countries.models.CountryUpdateLog)

```

    Updates happened with a country record
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|country |country |integer | | |True | |FK:countries.models.Country |
|note |note |text | | | |Both | |
|updated at |updated_at |timestamp with time zone | | | |Blank | |
|updated by |updated_by |integer | | |True |Both |FK:django.contrib.auth.models.User |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution(institutions.models.Institution)

```

    List of institutions reviewed or evaluated by EQAR registered agencies.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|deqar id |deqar_id |varchar(25) | | | |Blank | |
|eter id |eter_id |varchar(20) | | | |Both | |
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
|other comment |other_comment |text | | | |Blank | |
|internal note |internal_note |text | | | |Blank | |
|is other provider |is_other_provider |boolean | | | | | |
|organization type |organization_type |integer | | |True |Both |FK:institutions.models.InstitutionOrganizationType |
|source of information |source_of_information |varchar(200) | | | |Both | |
|created by |created_by |integer | | |True |Both |FK:django.contrib.auth.models.User |
|created at |created_at |timestamp with time zone | | | |Blank | |

Options
```
ordering : ('name_primary',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Identifier(institutions.models.InstitutionIdentifier)

```

    List of other (non-ETER) identifiers for the institution and the source of the identifier.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|identifier |identifier |varchar(100) | | | | | |
|agency |agency |integer | | |True |Both |FK:agencies.models.Agency |
|resource |resource |varchar(150) | | |True |Both |FK:lists.models.IdentifierResource |
|note |note |text | | | |Blank | |
|identifier valid from |identifier_valid_from |date | | | | | |
|identifier valid to |identifier_valid_to |date | | | |Both | |

Options
```
unique_together : (('institution', 'agency', 'resource'),)
ordering : ('agency', 'resource', 'identifier')
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Name(institutions.models.InstitutionName)

```

    List of names/acronym used for an institution in a particular period.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|name official |name_official |varchar(200) | | | | | |
|name official transliterated |name_official_transliterated |varchar(200) | | | |Blank | |
|name english |name_english |varchar(200) | | | |Blank | |
|acronym |acronym |varchar(30) | | | |Blank | |
|name source note |name_source_note |text | | | |Blank | |
|name valid to |name_valid_to |date | | | |Both | |
|orgreg char type |orgreg_char_type |jsonb | | | |Blank | |

Options
```
ordering : ('institution', 'name_official', 'name_english')
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Name Version(institutions.models.InstitutionNameVersion)

```

    Different versions of institution names with transliteration as applicable.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|institution name |institution_name |integer | | |True | |FK:institutions.models.InstitutionName |
|name |name |varchar(200) | | | | | |
|transliteration |transliteration |varchar(200) | | | |Blank | |
|name version source |name_version_source |varchar(20) | | | |Blank | |
|name version source note |name_version_source_note |text | | | |Blank | |

Options
```
ordering : ['-id']
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Country(institutions.models.InstitutionCountry)

```

    List of countries where the institution is located.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
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

Options
```
ordering : ['-id']
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution NQF Level(institutions.models.InstitutionNQFLevel)

```

    List of NQF levels that are valid for each institution.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|nqf level |nqf_level |varchar(10) | | | | | |
|nqf level source |nqf_level_source |varchar(20) | | | | | |
|nqf level source note |nqf_level_source_note |text | | | |Blank | |
|nqf level valid from |nqf_level_valid_from |date | | | | | |
|nqf level valid to |nqf_level_valid_to |date | | | |Both | |

Options
```
ordering : ['-id']
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution QF-EHEA Level(institutions.models.InstitutionQFEHEALevel)

```

    List of QF-EHEA levels that are valid for each institution.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|qf ehea level |qf_ehea_level |integer | | |True | |FK:lists.models.QFEHEALevel |
|qf ehea level source |qf_ehea_level_source |varchar(20) | | | | | |
|qf ehea level source note |qf_ehea_level_source_note |text | | | |Blank | |
|qf ehea level valid from |qf_ehea_level_valid_from |date | | | | | |
|qf ehea level valid to |qf_ehea_level_valid_to |date | | | |Both | |

Options
```
ordering : ['qf_ehea_level__code']
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Historical Relationship Type(institutions.models.InstitutionHistoricalRelationshipType)

```

    Historical relationship types between institutions
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|type from |type_from |varchar(200) | | | | | |
|type to |type_to |varchar(200) | | | | | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Historical Relationship(institutions.models.InstitutionHistoricalRelationship)

```

    Historical relationships between institutions
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|institution source |institution_source |integer | | |True | |FK:institutions.models.Institution |
|institution target |institution_target |integer | | |True | |FK:institutions.models.Institution |
|relationship type |relationship_type |integer | | |True | |FK:institutions.models.InstitutionHistoricalRelationshipType |
|relationship note |relationship_note |text | | | |Both | |
|relationship date |relationship_date |date | | | | | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Hierarchical Relationship Type(institutions.models.InstitutionHierarchicalRelationshipType)

```

    Hierarchical relationship types between institutions
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|type |type |varchar(200) | | | | | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Hierarchical Relationship(institutions.models.InstitutionHierarchicalRelationship)

```

    Hierarchical relationships between institutions
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|institution parent |institution_parent |integer | | |True | |FK:institutions.models.Institution |
|institution child |institution_child |integer | | |True | |FK:institutions.models.Institution |
|relationship type |relationship_type |integer | | |True |Both |FK:institutions.models.InstitutionHierarchicalRelationshipType |
|relationship note |relationship_note |text | | | |Both | |
|valid from |valid_from |date | | | |Both | |
|valid to |valid_to |date | | | |Both | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Organization Type(institutions.models.InstitutionOrganizationType)

```

    Organization types of institutions (for micro-credentials)
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|type |type |varchar(200) | | | | | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Historical Field(institutions.models.InstitutionHistoricalField)

```

    Name of the db_fields which can contain historical data of the institution.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|field |field |varchar(50) | | | | | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Flag(institutions.models.InstitutionFlag)

```

    Flags belonging to an institution
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|flag |flag |integer | | |True | |FK:lists.models.Flag |
|flag message |flag_message |text | | | |Blank | |
|active |active |boolean | | | | | |
|removed by eqar |removed_by_eqar |boolean | | | | | |
|created at |created_at |timestamp with time zone | | | |Blank | |
|updated at |updated_at |timestamp with time zone | | | |Blank | |

Options
```
unique_together : (('institution', 'flag_message'),)
ordering : ['id', 'flag__id']
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Historical Data(institutions.models.InstitutionHistoricalData)

```

    The historical data that institutions change.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|field |field |integer | | |True | |FK:institutions.models.InstitutionHistoricalField |
|record id |record_id |integer | | | |Both | |
|value |value |varchar(200) | | | | | |
|valid from |valid_from |date | | | |Both | |
|valid to |valid_to |date | | | |Both | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Institution Update Log(institutions.models.InstitutionUpdateLog)

```

    Updates happened with a report
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |
|note |note |text | | | |Both | |
|updated at |updated_at |timestamp with time zone | | | |Blank | |
|updated by |updated_by |integer | | |True |Both |FK:django.contrib.auth.models.User |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Language(lists.models.Language)

```
Language(id, iso_639_1, iso_639_2, language_name_en)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|iso 639 1 |iso_639_1 |varchar(10) | | | | | |
|iso 639 2 |iso_639_2 |varchar(10) | | | |Blank | |
|language name en |language_name_en |varchar(100) | |True | | | |

Options
```
ordering : ('language_name_en',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## QF-EHEA level(lists.models.QFEHEALevel)

```
QFEHEALevel(id, code, level)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|code |code |integer | | | |Both | |
|level |level |varchar(20) | | | | | |

Options
```
ordering : ('code',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Association(lists.models.Association)

```
Association(id, association)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|association |association |varchar(200) | | | | | |

Options
```
ordering : ('association',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## EQAR Decision Type(lists.models.EQARDecisionType)

```
EQARDecisionType(id, type)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|type |type |varchar(25) | | | | | |

Options
```
ordering : ('type',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Identifier Resource(lists.models.IdentifierResource)

```
IdentifierResource(resource, title, source, link)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|resource |resource |varchar(150) |True |True | | | |
|title |title |varchar(300) | | | |Both | |
|source |source |text | | | |Both | |
|link |link |varchar(200) | | | |Both | |

Options
```
ordering : ('resource',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Permission Type(lists.models.PermissionType)

```
PermissionType(id, type)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|type |type |varchar(50) | | | | | |

Options
```
ordering : ('type',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Flag(lists.models.Flag)

```
Flag(id, flag)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|flag |flag |varchar(20) | | | | | |

Options
```
ordering : ('id', 'flag')
default_permissions : ('add', 'change', 'delete', 'view')
```


## Degree Outcome(lists.models.DegreeOutcome)

```
DegreeOutcome(id, outcome)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|outcome |outcome |varchar(80) | | | | | |

Options
```
ordering : ('outcome',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Assessment and Certification(lists.models.Assessment)

```
Assessment(id, assessment)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|assessment |assessment |varchar(50) | | | | | |

Options
```
ordering : ('assessment',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Cross-border QA Possibility(lists.models.CrossBorderPossibility)

```
CrossBorderPossibility(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Cross-border QA Approval(lists.models.CrossBorderApproval)

```
CrossBorderApproval(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Cross-border QA Requirement(lists.models.CrossBorderRequirement)

```
CrossBorderRequirement(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Cross-border QA Criteria(lists.models.CrossBorderCriteria)

```
CrossBorderCriteria(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Cross-border QA Decision(lists.models.CrossBorderDecision)

```
CrossBorderDecision(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## European Approach Possibility(lists.models.EuropeanApproachPossibility)

```
EuropeanApproachPossibility(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## TNE Possibility(lists.models.TnePossible)

```
TnePossible(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## TNE Approval (outgoing)(lists.models.TneApprovalOutgoing)

```
TneApprovalOutgoing(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## TNE QA Regime (outgoing)(lists.models.TneQaOutgoing)

```
TneQaOutgoing(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## TNE Origin Country Group(lists.models.TneOriginGroup)

```
TneOriginGroup(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## TNE Approval (incoming)(lists.models.TneApprovalIncoming)

```
TneApprovalIncoming(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## TNE QA Regime (incoming)(lists.models.TneQaIncoming)

```
TneQaIncoming(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Micro-credential QA Regime(lists.models.McQa)

```
McQa(id, title, uri, description)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|title |title |varchar(255) | | | | | |
|uri |uri |varchar(255) | | | |Both | |
|description |description |text | | | |Blank | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## programme-country relationship(programmes.models.Programme_countries)

```
Programme_countries(id, programme, country)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|programme |programme |integer | | |True | |FK:programmes.models.Programme |
|country |country |integer | | |True | |FK:countries.models.Country |

Options
```
unique_together : (('programme', 'country'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Programmme(programmes.models.Programme)

```

    Institutional programmes or joint-programmes evaluated in reports.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|name primary |name_primary |varchar(255) | | | |Blank | |
|nqf level |nqf_level |varchar(255) | | | |Blank | |
|qf ehea level |qf_ehea_level |integer | | |True |Both |FK:lists.models.QFEHEALevel |
|degree outcome |degree_outcome |integer | | |True | |FK:lists.models.DegreeOutcome |
|workload ects |workload_ects |integer | | | |Both | |
|assessment certification |assessment_certification |integer | | |True |Both |FK:lists.models.Assessment |
|field study |field_study |varchar(70) | | | |Both | |
|field study title |field_study_title |varchar(300) | | | |Both | |
|learning outcome description |learning_outcome_description |text | | | |Both | |
|mc as part of accreditation |mc_as_part_of_accreditation |boolean | | | | | |
|countries |countries | | | | |Blank |M2M:countries.models.Country (through: programmes.models.Programme_countries) |

Options
```
ordering : ['id', 'report']
default_permissions : ('add', 'change', 'delete', 'view')
```


## Programme Name(programmes.models.ProgrammeName)

```

    One or more names of institutional programmes.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|programme |programme |integer | | |True | |FK:programmes.models.Programme |
|name |name |varchar(255) | | | |Both | |
|name is primary |name_is_primary |boolean | | | | | |
|qualification |qualification |varchar(255) | | | |Both | |

Options
```
unique_together : (('programme', 'name'),)
ordering : ('-name_is_primary', 'name')
default_permissions : ('add', 'change', 'delete', 'view')
```


## Programme Identifier(programmes.models.ProgrammeIdentifier)

```

    List of identifiers for the programme and the source of the identifier.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|programme |programme |integer | | |True | |FK:programmes.models.Programme |
|identifier |identifier |varchar(50) | | | | | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|resource |resource |varchar(200) | | | |Blank | |

Options
```
unique_together : (('programme', 'agency', 'resource'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Programme Learning Outcome(programmes.models.ProgrammeLearningOutcome)

```

    List of learning outcomes from the ESCO terminology
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|programme |programme |integer | | |True | |FK:programmes.models.Programme |
|learning outcome esco |learning_outcome_esco |varchar(70) | | | |Both | |
|learning outcome esco title |learning_outcome_esco_title |varchar(300) | | | |Both | |

Options
```
unique_together : (('programme', 'learning_outcome_esco'),)
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## report-agency relationship(reports.models.Report_contributing_agencies)

```
Report_contributing_agencies(id, report, agency)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |

Options
```
unique_together : (('report', 'agency'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## report-agencyesgactivity relationship(reports.models.Report_agency_esg_activities)

```
Report_agency_esg_activities(id, report, agencyesgactivity)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|agencyesgactivity |agencyesgactivity |integer | | |True | |FK:agencies.models.AgencyESGActivity |

Options
```
unique_together : (('report', 'agencyesgactivity'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## report-institution relationship(reports.models.Report_institutions)

```
Report_institutions(id, report, institution)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |

Options
```
unique_together : (('report', 'institution'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## report-institution relationship(reports.models.Report_platforms)

```
Report_platforms(id, report, institution)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|institution |institution |integer | | |True | |FK:institutions.models.Institution |

Options
```
unique_together : (('report', 'institution'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Report(reports.models.Report)

```

    List of reports and evaluations produced on HE institutions by EQAR registered agencies.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|agency |agency |integer | | |True | |FK:agencies.models.Agency |
|local identifier |local_identifier |varchar(255) | | | |Both | |
|status |status |integer | | |True | |FK:reports.models.ReportStatus |
|decision |decision |integer | | |True | |FK:reports.models.ReportDecision |
|summary |summary |text | | | |Both | |
|valid from |valid_from |date | | | | | |
|valid to |valid_to |date | | | |Both | |
|flag |flag |integer | | |True | |FK:lists.models.Flag |
|flag log |flag_log |text | | | |Blank | |
|other comment |other_comment |text | | | |Both | |
|internal note |internal_note |text | | | |Both | |
|created at |created_at |timestamp with time zone | | | |Blank | |
|created by |created_by |integer | | |True |Both |FK:django.contrib.auth.models.User |
|updated at |updated_at |timestamp with time zone | | | | | |
|updated by |updated_by |integer | | |True |Both |FK:django.contrib.auth.models.User |
|contributing agencies |contributing_agencies | | | | |Blank |M2M:agencies.models.Agency (through: reports.models.Report_contributing_agencies) |
|agency esg activities |agency_esg_activities | | | | | |M2M:agencies.models.AgencyESGActivity (through: reports.models.Report_agency_esg_activities) |
|institutions |institutions | | | | | |M2M:institutions.models.Institution (through: reports.models.Report_institutions) |
|platforms |platforms | | | | |Blank |M2M:institutions.models.Institution (through: reports.models.Report_platforms) |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Report Status(reports.models.ReportStatus)

```

    Status of the reports.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|status |status |varchar(50) | | | | | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Report Decision(reports.models.ReportDecision)

```

    Decision described in the report.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|decision |decision |varchar(50) | | | | | |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


## Report Link(reports.models.ReportLink)

```

    Links to records on individual reports and evaluations at agency’s site.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|link display name |link_display_name |varchar(200) | | | |Both | |
|link |link |varchar(255) | | | |Both | |

Options
```
ordering : ('id',)
default_permissions : ('add', 'change', 'delete', 'view')
```


## reportfile-language relationship(reports.models.ReportFile_languages)

```
ReportFile_languages(id, reportfile, language)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |integer |True |True | |Blank | |
|reportfile |reportfile |integer | | |True | |FK:reports.models.ReportFile |
|language |language |integer | | |True | |FK:lists.models.Language |

Options
```
unique_together : (('reportfile', 'language'),)
default_permissions : ('add', 'change', 'delete', 'view')
```


## Report File(reports.models.ReportFile)

```

    PDF versions of reports and evaluations.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|file display name |file_display_name |varchar(255) | | | |Blank | |
|file original location |file_original_location |varchar(500) | | | |Blank | |
|file |file |varchar(255) | | | |Blank | |
|file checksum |file_checksum |varchar(32) | | | |Both | |
|download status |download_status |varchar(20) | | | |Blank |pending:Pending, success:Success, failed:Failed |
|languages |languages | | | | | |M2M:lists.models.Language (through: reports.models.ReportFile_languages) |

Options
```
ordering : ['id', 'report']
default_permissions : ('add', 'change', 'delete', 'view')
```


## Report Flag(reports.models.ReportFlag)

```

    Flags belonging to a report
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|flag |flag |integer | | |True | |FK:lists.models.Flag |
|flag message |flag_message |text | | | |Blank | |
|active |active |boolean | | | | | |
|removed by eqar |removed_by_eqar |boolean | | | | | |
|created at |created_at |timestamp with time zone | | | |Blank | |
|updated at |updated_at |timestamp with time zone | | | |Blank | |

Options
```
unique_together : (('report', 'flag_message'),)
ordering : ['id', 'flag__id']
default_permissions : ('add', 'change', 'delete', 'view')
```


## Report Update Log(reports.models.ReportUpdateLog)

```

    Updates happened with a report
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |integer |True |True | |Blank | |
|report |report |integer | | |True | |FK:reports.models.Report |
|note |note |text | | | |Both | |
|updated at |updated_at |timestamp with time zone | | | |Blank | |
|updated by |updated_by |integer | | |True |Both |FK:django.contrib.auth.models.User |

Options
```
default_permissions : ('add', 'change', 'delete', 'view')
```


