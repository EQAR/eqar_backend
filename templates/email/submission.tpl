{% extends "mail_templated/base.tpl" %}

{% block subject %}
    [DEQAR] - Submission report on {{ date }}
{% endblock %}

{% block html %}
    <h2>Dear Sender</h2>
    <p>The following reports were successfully submitted on {{ date }}
    <p><strong>Total number of accepted reports: {{ response|length }}</strong></p>

    {% for resp in response %}
        <p>
            <strong>Report - {{ resp.submitted_report.name }}</strong><br/>
            <i>Assigned report identifier in DEQAR:<i> {{ resp.submitted_report.id }}<br/>
            <i>Assigned flag:</i> {{ resp.report_flag }}<br/>
            <i>Sanity check status:</i> {{ resp.sanity_check_status }}<br/>
            <i>Warnings about the report:</i>
            <ul>
                {% for rw in report_warnings %}
                    <li>{{ rw }}</li>
                {% endfor %}
            </ul>
            <i>Identified / created institution records:</i>
            <ul>
                {% for inst in resp.submitted_report.institutions %}
                    <li>{{ inst.name_primary }} / DEQAR ID: {{ inst.deqar_id }}</li>
                {% endfor %}
            </ul>
            <i>Warnings about institution records:</i>
            <ul>
                {% for iw in institution_warnings %}
                    <li>{{ iw }}</li>
                {% endfor %}
            </ul>
        </p>
    {% endfor %}

    <p><strong>This message will be cc-d to {{ agency_email }} when the agency test starts.</strong></p>
{% endblock %}