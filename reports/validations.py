import datetime


def _to_date(value):
    if isinstance(value, datetime.datetime):
        return value.date()
    return value


def validate_report_dates_within_activity_windows(activities, valid_from, valid_to=None):
    errors = []
    valid_from = _to_date(valid_from)
    valid_to = _to_date(valid_to)

    for activity in activities:
        activity_start = _to_date(activity.activity_valid_from)
        activity_end = _to_date(activity.activity_valid_to or activity.agency.registration_valid_to)

        has_from_error = valid_from < activity_start or (activity_end and valid_from > activity_end)
        has_to_error = valid_to and (valid_to < activity_start or (activity_end and valid_to > activity_end))

        if has_from_error or has_to_error:
            if activity_end:
                period = f"{activity_start} to {activity_end}"
            else:
                period = f"{activity_start} onward"

            errors.append(
                f"Report validity dates must fall within the assigned activity validity period "
                f"(activity #{activity.id}: {period})."
            )

    return errors
