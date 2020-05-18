from twilio.rest import Client
import json
import os


if __name__ == '__main__':
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_ACCOUNT_TOKEN')
    client = Client(account_sid, auth_token)
    file = open('studio/bot_flow.json')
    definition = file.read()
    prod_definition = definition.replace('accfb-foodnow-stage', 'accfb-foodnow')
    flowdef = json.loads(prod_definition)
    client.studio.flows.create(commit_message='Import FoodNow flow', friendly_name='foodnow_bot', status='published', definition=flowdef)
