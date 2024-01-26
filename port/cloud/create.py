#if you are working locally, you can use smee.io to foward the webhook request to your localhost
# you can generate smee url by going to smee.getport.io
#
# running a smee client in your terminal:
# smee --url YOUR_SMEE_URL_HERE --target http://127.0.0.1:8000/

import requests

from port.consts import API_URL, TIMEOUT

def handle(request, headers):
    """Handle webhooks"""

    try:
        run_id = request.json.get('context').get('runId')
        insert_logs_endpoint = f"{API_URL}/actions/runs/{run_id}/logs"
        update_run_endpoint = f"{API_URL}/actions/runs/{run_id}"
        blueprint_id = request.get_json()['context']['blueprint']
        title = request.get_json()['payload']['properties']['title']
        crif_project = request.get_json()['payload']['properties']['crif_project']
        resource_name = request.get_json()['payload']['properties']['resource_name']

		# CREATE entity
        create_entity_endpoint = f"{API_URL}/blueprints/{blueprint_id}/entities?create_missing_related_entities=true&run_id={run_id}"
        create_entity_response = requests.post(create_entity_endpoint, json={
            "identifier":resource_name,
            "title":title,
            "properties":{
                "readme":"string",
                "url":"https://example.com",
                "language":"string",
                "slack":"https://example.com",
                "tier":"Mission Critical"
            },
            "relations": {
                "project": crif_project
            }
        }, headers=headers
        , timeout=TIMEOUT)
        create_entity_response.raise_for_status()

        # create entity
        print('Successfully created the entity')
        requests.post(insert_logs_endpoint, json={
            "message": "Successfully created the entity"
        }, headers=headers
        , timeout=TIMEOUT)

        # create run log
        print('Successfully created run log')
        requests.post(insert_logs_endpoint, json={
            "message": "Successfully created run log"
        }, headers=headers
        , timeout=TIMEOUT)

		# update the status of the run
        print('Successfully updated the run status')
        requests.post(insert_logs_endpoint, json={
            "message": "Successfully updated the run status"
        }, headers=headers
        , timeout=TIMEOUT)

		# SUCCESS entity
        requests.patch(update_run_endpoint, json={
            "status": "SUCCESS"
        }, headers=headers
        , timeout=TIMEOUT)

    except Exception as e:
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

        raise SystemError('Something went wrong', str(e)) from e

    return 'OK'
