from flask_restful import Resource
from flask import request, abort
from twilio.request_validator import RequestValidator
import os
import googlemaps
import json
from foodnow.db import get_postgres_client


class FindPantryResource(Resource):
    def post(self):
        google_api_key = os.environ.get("GOOGLE_API_TOKEN")
        twilio_signature = request.headers['X-Twilio-Signature']
        twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        validator = RequestValidator(twilio_auth_token)
        url = request.url
        content = request.form
        if validator.validate(url, content, twilio_signature):
            memory = json.loads(content.get('Memory'))
            location = memory.get('twilio').get('collected_data').get('user_location').get('answers')
            city = location.get('city').get('answer')
            address = location.get('address').get('answer')
            formatted_address = '{}, {}, {}'.format(address, city, 'CA')
            gmaps = googlemaps.Client(key=google_api_key)
            geocode = gmaps.geocode(formatted_address)
            geolocation = geocode[0].get('geometry').get('location')
            print(geolocation)
        else:
            abort(401, 'Request not validated')


