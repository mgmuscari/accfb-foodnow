from flask_restful import Resource
from flask import request, abort, make_response
from flask import jsonify
from foodnow.db.distribution_site_dao import DistributionSiteDao
import os
import googlemaps
from googlemaps.exceptions import Timeout, TransportError, ApiError
from foodnow.db import get_postgres_client
import logging
import datetime
import math
from fractions import Fraction
import pytz


class FindPantryResource(Resource):

    @staticmethod
    def meters_to_miles(meters):
        distance = (meters / 1000.0) * 0.621371
        miles = math.floor(distance)
        miles_fraction = distance - miles
        fraction = Fraction(int(round(miles_fraction * 4)), 4)
        fraction_text = ''
        if fraction.numerator > 0 and fraction.denominator > 1:
            denoms = {2: 'half', 4: 'quarter'}
            fraction_text = '{} {}'.format(fraction.numerator, denoms[fraction.denominator])
            if fraction.numerator > 1:
                fraction_text = fraction_text + 's'
        if miles == 0:
            if len(fraction_text) > 0:
                return fraction_text + ' of a mile'
            else:
                return '1 quarter of a mile'
        if miles == 1:
            unit = 'mile'
        else:
            unit = 'miles'
        if len(fraction_text) > 0:
            fraction_text = ' and ' + fraction_text
        return str(int(miles)) + fraction_text + ' ' + unit

    @staticmethod
    def site_response(site_summary, date):
        site = site_summary['site']
        day_of_week = date.strftime('%A')
        if day_of_week not in site.schedules.keys():
            raise Exception('Site is not open on this day')
        return {
            'distance': FindPantryResource.meters_to_miles(site_summary['distance']),
            'site_name': site.name,
            'site_address': site.address,
            'site_city': site.city,
            'site_open': site.schedules.get(day_of_week).open_time.strftime('%I:%M %p'),
            'site_close': site.schedules.get(day_of_week).close_time.strftime('%I:%M %p'),
            'day_of_week': day_of_week
        }

    def get(self):
        google_api_key = os.environ.get("GOOGLE_API_TOKEN")
        try:
            with get_postgres_client() as pgclient:
                city = request.args.get("city")
                address = request.args.get("address")
                try:
                    formatted_address = '{}, {}, {}'.format(address, city, 'CA')
                    gmaps = googlemaps.Client(key=google_api_key)
                    geocode = gmaps.geocode(formatted_address)
                    geolocation = geocode[0].get('geometry').get('location')
                except (ApiError, Timeout, TransportError) as e:
                    logging.exception("Encountered an exception while geocoding the user's address")
                    return make_response("An error occurred", 500)

                dao = DistributionSiteDao(pgclient)

                today = datetime.datetime.now(tz=pytz.timezone("America/Los_Angeles")).date()
                tomorrow = today + datetime.timedelta(days=1)
                day_after = today + datetime.timedelta(days=2)

                sites_today = dao.find_open_sites_now(geolocation['lat'], geolocation['lng'])
                sites_tomorrow = dao.find_open_sites_on_day(geolocation['lat'], geolocation['lng'], tomorrow)
                sites_day_after = dao.find_open_sites_on_day(geolocation['lat'], geolocation['lng'], day_after)

                site_responses_today = [FindPantryResource.site_response(site_summary, today) for site_summary in sites_today.values()]
                site_responses_tomorrow = [FindPantryResource.site_response(site_summary, tomorrow) for site_summary in sites_tomorrow.values()]
                site_responses_day_after = [FindPantryResource.site_response(site_summary, day_after) for site_summary in sites_day_after.values()]

                site_responses = {
                    "sites": site_responses_today + site_responses_tomorrow + site_responses_day_after
                }

                if len(site_responses) > 0:
                    return jsonify(site_responses)
                else:
                    return make_response("No sites were found", 404)
        except Exception as e:
            logging.exception("Encountered an exception while finding a pantry")
            return make_response("An error occurred", 500)




