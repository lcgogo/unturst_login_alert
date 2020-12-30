import json
import requests

from local_settings import PAGERDUTY_API_ACCESS_KEY, PAGERDUTY_ROUTING_KEY


def trigger_incident(summary):
    headers = {
        'Authorization': 'Token token={}'.format(PAGERDUTY_API_ACCESS_KEY),
        'Content-type': 'application/json',
    }
    data = {
        "payload": {
            "summary": summary,
            "source": "test",
            "severity": "warning"
        },
        "routing_key": PAGERDUTY_ROUTING_KEY,
        "event_action": "trigger"
    }
    r = requests.post(
        'https://events.pagerduty.com/v2/enqueue',
        data=json.dumps(data),
        headers=headers,
    )
