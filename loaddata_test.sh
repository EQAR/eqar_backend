#!/usr/bin/env bash
python manage.py loaddata flag
python manage.py loaddata permission_type

python manage.py loaddata association
python manage.py loaddata eqar_decision_type
python manage.py loaddata identifier_resource
python manage.py loaddata language
python manage.py loaddata qf_ehea_level

python manage.py loaddata agency_activity_type
python manage.py loaddata agency_focus

python manage.py loaddata country_historical_field
python manage.py loaddata country_qa_requirement_type
python manage.py loaddata country
python manage.py loaddata country_historical_data_demo_01

python manage.py loaddata report_decision
python manage.py loaddata report_status

python manage.py loaddata agency_historical_field

python manage.py loaddata agency_demo_01
python manage.py loaddata agency_demo_02

python manage.py loaddata submitting_agency_demo

python manage.py loaddata eter_demo
python manage.py loaddata institution_historical_field
python manage.py loaddata institution_relationship_type
python manage.py loaddata institution_hierarchical_relationship_type

python manage.py loaddata institution_demo_01
python manage.py loaddata institution_demo_02
python manage.py loaddata institution_demo_03

python manage.py loaddata report_demo_01

python manage.py loaddata programme_demo_01
python manage.py loaddata programme_demo_02
python manage.py loaddata programme_demo_03
python manage.py loaddata programme_demo_04
python manage.py loaddata programme_demo_05
python manage.py loaddata programme_demo_06
python manage.py loaddata programme_demo_07
python manage.py loaddata programme_demo_08
python manage.py loaddata programme_demo_09
python manage.py loaddata programme_demo_10
python manage.py loaddata programme_demo_11
python manage.py loaddata programme_demo_12