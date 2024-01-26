#if you are working locally, you can use smee.io to foward the webhook request to your localhost
# you can generate smee url by going to smee.getport.io
#
# running a smee client in your terminal:
# smee --url YOUR_SMEE_URL_HERE --target http://127.0.0.1:8000/
import requests

from port.consts import API_URL, TIMEOUT

def handle(request, headers):
    """Handle webhooks"""

    run_id = request.json.get('context').get('runId')
    insert_logs_endpoint = f"{API_URL}/actions/runs/{run_id}/logs"
    update_run_endpoint = f"{API_URL}/actions/runs/{run_id}"

    # update the status of the run to FAILURE
    requests.post(insert_logs_endpoint, json={
        "message": "Something went wrong"
    }, headers=headers
    , timeout=TIMEOUT)

    # FAILURE entity
    requests.patch(update_run_endpoint, json={
        "status": "FAILURE"
    }, headers=headers
    , timeout=TIMEOUT)

    raise SystemError('Invalid Action')
