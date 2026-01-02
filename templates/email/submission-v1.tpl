{% extends "mail_templated/base.tpl" %}

{% block subject %}
    [DEQAR] - Submission report on {{ date }}
{% endblock %}

{% block html %}
    <h2>Dear Sender</h2>

    <!-- API deprecation warning -->
    <p style="color:#b30000; font-weight:bold; border:2px solid #b30000; padding:10px; background-color:#fff5f5;">
        IMPORTANT API DEPRECATION NOTICE<br/><br/>
        You have submitted your package using <strong>Submission API v1</strong>.<br/>
        <strong>This endpoint will be permanently terminated on 1 February 2026.</strong><br/><br/>
        Any submissions sent to v1 after this date will no longer be processed.
        Please migrate as soon as possible to the <strong>Submission API v2</strong>.<br/><br/>
        The full API documentation for v2 is available here:<br/>
        <a href="https://backend.deqar.eu/submissionapi/v2/swagger/" target="_blank">
            https://backend.deqar.eu/submissionapi/v2/swagger/
        </a>
    </p>

    <p>The following reports were submitted on {{ date }}

    <p>
        <strong>SUBMISSION INGEST SUMMARY</strong><br/>
        <strong>Total number of reports submitted: {{ total_submission }}</strong><br/>
        Total accepted: {{ total_accepted }}<br/>
        Total rejected: {{ total_rejected }}<br/>
        <strong>Total number of institution records identified or created: {{ institution_total}}</strong><br/>
        Total existing institution records identified: {{ institution_existing }}<br/>
        Total new institution records created: {{ institution_new }}<br/>
    </p>
    <hr/>
    {% for resp in response %}
        <p>
            <strong>Report - {{ resp.submitted_report.name }}</strong><br/>
            <i>Assigned report identifier in DEQAR:<i> {{ resp.submitted_report.id }}<br/>
            <i>Institution record:</i>
            <ul>
                {% for inst in resp.submitted_report.institutions %}
                    <li>
                        {{ inst.name_primary }} ({{ inst.deqar_id }})
                        {% if inst.id > max_inst_id %}
                            <span style="color:red;">new record!</span>
                        {% endif %}
                    </li>
                {% endfor %}
            </ul>
            <i>Sanity check status:</i> {{ resp.sanity_check_status }}<br/>
            <i>Assigned flag:</i> {{ resp.report_flag }}<br/><br/>

            {% if resp.report_warnings %}
            <i>Problem(s) identified with submitted report data:</i>
            <ul>
                {% for rw in resp.report_warnings %}
                    <li>{{ rw }}</li>
                {% endfor %}
            </ul>
            {% endif %}

            {% if resp.institution_warnings %}
            <i>Problem(s) identified with submitted institution data:</i>
            <ul>
                {% for iw in resp.institution_warnings %}
                    <li>{{ iw }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </p>
        <hr/>
    {% endfor %}
{% endblock %}