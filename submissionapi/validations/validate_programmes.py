from rest_framework import serializers

def validate_programmes(data):
    errors = {}

    qf_ehea_level = data.get('qf_ehea_level')
    degree_outcome = data.get('degree_outcome')
    workload_ects = data.get('workload_ects')
    assessment_certification = data.get('assessment_certification')

    # Additional programme data fields are required if degree outcome is "no full degree"
    if degree_outcome:
        if degree_outcome.id == 2:
            if not workload_ects:
                errors["workload_ects"] = "ECTS credits are required, when degree_outcome field is " \
                                          "'2 / no full degree'"
            if not assessment_certification:
                errors["assessment_certification"] = "Assessment information is required, " \
                                                     "when degree_outcome field is '2 / no full degree'."
            if not qf_ehea_level:
                errors["qf_ehea_level"] = "QF-EHEA Level information is required, " \
                                          "when degree_outcome field is '2 / no full degree'."

    if len(errors) > 0:
        raise serializers.ValidationError(errors)

    return data