{% extends "mail_templated/base.tpl" %}

{% block subject %}
    [DEQAR] - Your report validation raised a red flag
{% endblock %}

{% block html %}
    <h2>Dear Sender</h2>
    <p>The following report(s) you submitted on {{ date }} raised a red flag during the validation process.
    Please review the identified issues and take necessary actions to resolve them.</p>

    <strong>Report - {{ report.name }}</strong><br/><br/>
    <i>Assigned report identifier in DEQAR:<i> {{ report.id }}<br/>
    <i>Red flag reason:</i> {{ flag_message }}<br/><br/>
{% endblock %}