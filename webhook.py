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
from port.consts import API_URL, CLIENT_ID, CLIENT_SECRET, PORT, TIMEOUT

from port.default.action import handle as default_handle
from port.project.create import handle as create_crif_project_web_hook
from port.cloud.create import handle as create_s3_bucket
from port.service.scaffold import handle as scaffold_java_service_web_hook

app = Flask(__name__)

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

    action = request.json.get('action')

    match action:
        case "scaffold_java_service_web_hook":
            result = scaffold_java_service_web_hook(request, headers)
        case "create_s3_bucket":
            result = create_s3_bucket(request, headers)
        case "create_crif_project_web_hook":
            result = create_crif_project_web_hook(request, headers)
        case _:
            default_handle(request, headers)

    return result

if __name__ == '__main__':
    app.run(port=PORT)
