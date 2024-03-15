from rest_framework import serializers


def validate_identifiers_and_resource(value):
    # Validate if there is only one identifier without resource id
    count = 0
    resources = []
    for identifier in value:
        if 'resource' not in identifier.keys():
            count += 1
        else:
            resources.append(identifier['resource'])
    if count > 1:
        raise serializers.ValidationError("You can only submit one identifier without resource.")

    # Validate if resource values are unique
    if len(resources) != len(set(resources)):
        raise serializers.ValidationError("You can only submit different type of resources.")
    return value
