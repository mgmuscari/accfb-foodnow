from flask_restful import Resource
from flask import request, abort, make_response
from twilio.request_validator import RequestValidator
import os
import json
from json import JSONDecodeError
from foodnow.model.responses import Responses
from foodnow.db import get_postgres_client
import logging

class ValidCityResource(Resource):

    def post(self):
        twilio_signature = request.headers['X-Twilio-Signature']
        twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        validator = RequestValidator(twilio_auth_token)
        url = request.url
        content = request.form
        if validator.validate(url, content, twilio_signature):
            try:
                try:
                    memory = json.loads(content.get('Memory'))
                    location = memory.get('twilio').get('collected_data').get('user_location').get('answers')
                    city = location.get('city').get('answer')
                except (JSONDecodeError, AttributeError) as e:
                    logging.exception("Encountered error parsing Twilio callback")
                    return make_response(json.dumps(Responses.error_response()), 200)

                with get_postgres_client() as pgclient:
                    if ValidCityResource.valid_city(pgclient, city):
                        return make_response(json.dumps(Responses.valid_city_response(city)), 200)
                    else:
                        return make_response(json.dumps(Responses.invalid_city_response()), 200)
            except Exception as e:
                logging.exception("An error occurred validating the user's city")
                return make_response(json.dumps(Responses.error_response()), 200)

    @staticmethod
    def valid_city(pgclient, city):
        select = 'select * from accfb.cities where lower(name)=lower(%(city)s)'
        with pgclient.cursor() as cursor:
            cursor.execute(select, {'city': city})
            row = cursor.fetchone()
            return row is not None
        return False
