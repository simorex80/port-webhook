#if you are working locally, you can use smee.io to foward the webhook request to your localhost
# you can generate smee url by going to smee.getport.io
#
# running a smee client in your terminal:
# smee --url YOUR_SMEE_URL_HERE --target http://127.0.0.1:8000/

import hashlib
import hmac
import json
import base64
import requests
from flask import Flask, request

CLIENT_ID = "EZ3X0Fu19vAEZgAJIRL9LrB8P7Erpx1J"
CLIENT_SECRET = "5aJ1Dxs1fTp4RWxBBhG9OeAbF5PiNkAFmgQ9aTxOYf1fbPe2lvzHtRjMvJgVjuJB"

API_URL = "https://api.getport.io/v1"

app = Flask(__name__)
PORT = 8000
TIMEOUT = 30

@app.route('/', methods=['POST'])
def handle_webhooks():
    """Handle webhooks"""

    # webhook signature validation
    message = f"{
            request.headers['x-port-timestamp']
        }.{
            json.dumps(request.get_json(), separators=(',', ':'))
        }"
    signed = hmac.new(CLIENT_SECRET.encode('utf-8'), digestmod=hashlib.sha256)
    signed.update(message.encode('utf-8'))

    decoded_signed = base64.b64encode(signed.digest()).decode()

    signature = request.headers['x-port-signature'].split(',')[1]

    if decoded_signed == signature:
        print('Webhook signature validated successfully')
    else:
        raise ValueError('Invalid webhook signature')
    # webhook signature validation

    # You can put any custom logic here

    # This part is used to update the run status
    access_token_response = requests.post(f"{API_URL}/auth/access_token", json={
        "clientId": CLIENT_ID,
        "clientSecret": CLIENT_SECRET
    }, timeout=TIMEOUT)
    token = access_token_response.json().get('accessToken')
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        run_id = request.json.get('context').get('runId')
        insert_logs_endpoint = f"{API_URL}/actions/runs/{run_id}/logs"
        update_run_endpoint = f"{API_URL}/actions/runs/{run_id}"
        blueprint_id = request.get_json()['context']['blueprint']
        resource_name = request.get_json()['payload']['properties']['resource_name']

		# CREATE entity
        create_entity_endpoint = f"{API_URL}/blueprints/{blueprint_id}/entities?create_missing_related_entities=true&run_id={run_id}"
        create_entity_response = requests.post(create_entity_endpoint, json={
            "identifier":resource_name,
            "title":"Some Title",
            "properties":{
                "readme":"string",
                "url":"https://example.com",
                "language":"string",
                "slack":"https://example.com",
                "tier":"Mission Critical"
            },
            "relations":{}
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


if __name__ == '__main__':
    app.run(port=PORT)
