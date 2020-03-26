from flask_restful import Resource
from flask import request, abort, make_response
from flask import jsonify
from twilio.request_validator import RequestValidator
from foodnow.model.responses import Responses
import os
import googlemaps
from googlemaps.exceptions import Timeout, TransportError, ApiError
import json
from json import JSONDecodeError
from foodnow.db import get_postgres_client
import logging


class FindPantryResource(Resource):

    def get(self):
        google_api_key = os.environ.get("GOOGLE_API_TOKEN")
        twilio_signature = request.headers['X-Twilio-Signature']
        twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        validator = RequestValidator(twilio_auth_token)
        url = request.url
        content = request.form
        if validator.validate(url, content, twilio_signature):
            try:
                with get_postgres_client() as pgclient:
                    try:
                        city = request.args.get("city")
                        address = request.args.get("address")
                    except (JSONDecodeError, AttributeError) as e:
                        logging.exception("Encountered an exception while parsing the Twilio callback")
                        return make_response("An error occurred", 500)

                    formatted_address = '{}, {}, {}'.format(address, city, 'CA')
                    try:
                        gmaps = googlemaps.Client(key=google_api_key)
                        geocode = gmaps.geocode(formatted_address)
                        geolocation = geocode[0].get('geometry').get('location')
                    except (ApiError, Timeout, TransportError) as e:
                        logging.exception("Encountered an exception while geocoding the user's address")
                        return make_response(json.dumps(Responses.error_response()), 200)

                    select = 'select name, address, city from accfb.distribution_sites order by st_distance(st_point(%(lng)s, %(lat)s), location) asc limit 1'
                    cursor = pgclient.cursor()
                    cursor.execute(select, geolocation)
                    result = cursor.fetchone()
                    (name, address, city) = result
                    return jsonify({"pantry_name": name, "pantry_address": address, "pantry_city": city})
            except Exception as e:
                logging.exception("Encountered an exception while finding a pantry")
                return make_response(json.dumps(Responses.error_response()), 200)
        else:
            abort(401, 'Request not validated')

    def post(self):
        google_api_key = os.environ.get("GOOGLE_API_TOKEN")
        twilio_signature = request.headers['X-Twilio-Signature']
        twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        validator = RequestValidator(twilio_auth_token)
        url = request.url
        content = request.form
        if validator.validate(url, content, twilio_signature):
            try:
                with get_postgres_client() as pgclient:
                    try:
                        memory = json.loads(content.get('Memory'))
                        location = memory.get('twilio').get('collected_data').get('user_location').get('answers')
                        city = location.get('city').get('answer')
                        address = location.get('address').get('answer')
                    except (JSONDecodeError, AttributeError) as e:
                        logging.exception("Encountered an exception while parsing the Twilio callback")
                        return make_response(json.dumps(Responses.error_response()), 200)

                    formatted_address = '{}, {}, {}'.format(address, city, 'CA')
                    try:
                        gmaps = googlemaps.Client(key=google_api_key)
                        geocode = gmaps.geocode(formatted_address)
                        geolocation = geocode[0].get('geometry').get('location')
                    except (ApiError, Timeout, TransportError) as e:
                        logging.exception("Encountered an exception while geocoding the user's address")
                        return make_response(json.dumps(Responses.error_response()), 200)

                    select = 'select name, address, city from accfb.distribution_sites order by st_distance(st_point(%(lng)s, %(lat)s), location) asc limit 1'
                    cursor = pgclient.cursor()
                    cursor.execute(select, geolocation)
                    result = cursor.fetchone()
                    (name, address, city) = result
                    response = Responses.found_pantry_response(name, address, city, formatted_address, geolocation)
                    return make_response(json.dumps(response), 200)
            except Exception as e:
                logging.exception("Encountered an exception while finding a pantry")
                return make_response(json.dumps(Responses.error_response()), 200)
        else:
            abort(401, 'Request not validated')



