import json
import requests

from local_settings import PAGERDUTY_ROUTING_KEY
from local_settings import HOSTNAME, HOSTIP


def trigger_incident(summary):
    headers = {
        'Content-type': 'application/json',
    }
    data = {
        "payload": {
            "summary": HOSTNAME + " " + HOSTIP + " " + summary,
            "source": HOSTNAME + " " + HOSTIP,
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
