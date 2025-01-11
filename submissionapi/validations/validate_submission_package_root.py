from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from reports.models import Report


def validate_submission_package_root(data):
    # Array to hold errors
    errors = []

    # Get the required values for the validations
    institutions = data.get('institutions', [])
    programmes = data.get('programmes', [])
    activities = data.get('activities', [])
    esg_activity = data.get('esg_activity', None)
    agency = data.get('agency', None)
    contributing_agencies = data.get('contributing_agencies', [])
    report = data.get('report_id', None)
    local_identifier = data.get('local_identifier', None)
    valid_from = data.get('valid_from')
    valid_to = data.get('valid_to', None)
    status = data.get('status', None)

    # Validate if every agency has at least one activity in the list. (Only for API v2)
    if not esg_activity:
        agencies_from_activities = []
        for activity in activities:
            agencies_from_activities.append(activity.agency.id)

        if agency.id not in agencies_from_activities:
            errors.append("Please provide at least one activity for the agency.")

        for ca in contributing_agencies:
            if ca.id not in agencies_from_activities:
                errors.append("Please provide at least one activity for the contributing agency.")

    #
    # Validate if activity types haas the right amount of programme and instituton records
    #
    # institutional
    if esg_activity:
        activity_type_id = esg_activity.activity_type_id
    else:
        activity_type_id = calculate_activity_type_id(activities)

    if activity_type_id == 2:
        if len(programmes) > 0:
            errors.append("Please remove programme information "
                          "with this particular Activity type.")
    # programme or institutional/programme
    elif activity_type_id == 1 or activity_type_id == 4:
        if len(institutions) > 1:
            errors.append("Please provide only one institution "
                          "with this particular Activity type.")
        if len(programmes) == 0:
            errors.append("Please provide at least one programme "
                          "with this particular Activity type.")
    # joint programme
    else:
        if len(institutions) == 1:
            errors.append("Please provide data for all of the institutions "
                          "with this particular Activity type.")
        if len(programmes) == 0:
            errors.append("Please provide at least one programme "
                          "with this particular Activity type.")

    #
    # Validate if report_id and local_identifier resolving to the same record,
    # or local_identifier is non-existent
    #
    if report and local_identifier:
        try:
            report_with_local_id = Report.objects.get(agency=agency, local_identifier=local_identifier)
            if report.id != report_with_local_id.id:
                errors.append("The submitted report_id is pointing to a different report, "
                              "than the submitted local identifier.")
        except ObjectDoesNotExist:
            pass

    #
    # Validate if valid_to date is larger than valid_from
    #
    date_from = datetime.strptime(valid_from, "%Y-%m-%d")

    if valid_to:
        date_to = datetime.strptime(valid_to, "%Y-%m-%d")
        if date_from >= date_to:
            errors.append("Report's validity start should be earlier then validity end.")

    #
    # Validate if Agency registration start is earlier than report validation start date.
    #
    if date_from:
        if agency.registration_valid_to:
            if not (agency.registration_start <= datetime.date(date_from) <= agency.registration_valid_to):
                errors.append("Report's validity date must fall between the Agency EQAR registration dates.")
        else:
            if agency.registration_start >= datetime.date(date_from):
                errors.append("Report's validity date must fall after the Agency was registered with EQAR.")

    #
    # Validations for OTHER PROVIDERS
    #
    # Check if all institutions are AP
    all_ap = True
    all_hei = True
    for i in institutions:
        if not i.is_other_provider:
            all_ap = False
        else:
            all_hei = False

    # Status must be 'voluntary' if all institutions are AP
    if all_ap:
        if not status or status.id != 2:
            errors.append("Status should be 'voluntary' if all organisations are other providers.")

    # Programme degree outcome must be "no full degree" for AP:
    if all_ap and len(programmes) > 0:
        for programme in programmes:
            if programme['degree_outcome'].id != 2:
                errors.append("Degree outcome should be '2 / no full degree' if all the "
                              "organisations are other providers")

    if len(errors) > 0:
        raise serializers.ValidationError({settings.NON_FIELD_ERRORS_KEY: errors})

    return data

def calculate_activity_type_id(activities):
    # Default = institutional
    activity_type_id = 2
    for activity in activities:
        # If there is a programme or institutional/programme activity, set the activity type to programme
        # if there was no joint/programme activity before
        if activity.activity_type_id == 1 or activity.activity_type_id == 4:
            if activity_type_id == 2:
                activity_type_id = activity.activity_type_id
        # If there is a joint/programme activity, set the activity type to joint programme
        # all the time
        elif activity.activity_type_id == 3:
            activity_type_id = 3
    return activity_type_id