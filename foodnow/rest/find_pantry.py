from flask_restful import Resource
from flask import request
from twilio.request_validator import RequestValidator
import os
from foodnow.db import get_postgres_client


class FindPantryResource(Resource):
    def post(self):
        twilio_signature = request.headers['X-Twilio-Signature']
        twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        validator = RequestValidator(twilio_auth_token)
        url = request.url
        content = request.form
        print(validator.validate(url, content, twilio_signature))
