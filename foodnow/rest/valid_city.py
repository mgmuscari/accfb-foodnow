from flask_restful import Resource
from flask import request, abort, make_response
from flask import jsonify
from twilio.request_validator import RequestValidator
import os
import json
from json import JSONDecodeError
from foodnow.model.responses import Responses
from foodnow.db import get_postgres_client
import logging

class ValidCityResource(Resource):

    def get(self):
        twilio_signature = request.headers['X-Twilio-Signature']
        twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        validator = RequestValidator(twilio_auth_token)
        url = request.url
        content = request.form
        if validator.validate(url, content, twilio_signature):
            try:
                city = request.args.get("city")
                with get_postgres_client() as pgclient:
                    if ValidCityResource.valid_city(pgclient, city):
                        return jsonify({"valid_city": "true", "city": city})
                    else:
                        return jsonify({"valid_city": "false", "city": city})

            except Exception as e:
                logging.exception("An error occurred validating the user's city")
                return make_response("An error occurred", 500)

    @staticmethod
    def valid_city(pgclient, city):
        city = city.strip()
        select = 'select * from accfb.cities where lower(name)=lower(%(city)s)'
        with pgclient.cursor() as cursor:
            cursor.execute(select, {'city': city})
            row = cursor.fetchone()
            return row is not None
        return False
