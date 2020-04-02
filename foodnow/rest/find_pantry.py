from flask_restful import Resource
from flask import request, app, make_response
from flask import jsonify
from foodnow.db.postgres.distribution_site_dao import PostgresDistributionSiteDao
from foodnow.model.schedule import Schedule
import os
import googlemaps
from googlemaps.exceptions import Timeout, TransportError, ApiError
from foodnow.db import get_postgres_client
import datetime
import math
from fractions import Fraction
import pytz
import logging

log = logging.getLogger(__name__)

class FindPantryResource(Resource):

    @staticmethod
    def readable_distance(meters, language):
        total_distance = (meters / 1000.0)
        unit = 'kilómetro'
        if language == 'en_US':
            total_distance = total_distance * 0.621371
            unit = 'mile'
        unit_distance = math.floor(total_distance)
        unit_fraction = total_distance - unit_distance
        fraction = Fraction(int(round(unit_fraction * 4)), 4)
        fraction_text = ''
        if fraction.numerator > 0 and fraction.denominator > 1:
            if language == 'en_US':
                denoms = {2: 'half', 4: 'quarter'}
            else:
                denoms = {2: 'media', 4: 'cuarto'}
            fraction_text = '{} {}'.format(fraction.numerator, denoms[fraction.denominator])
            if fraction.numerator > 1:
                fraction_text = fraction_text + 's'
        if unit_distance == 0:
            if len(fraction_text) > 0:
                if language == 'en_US':
                    return fraction_text + ' of a ' + unit
                else:
                    return fraction_text + ' de ' + unit
            else:
                if language == 'en_US':
                    return '1 quarter of a mile'
                else:
                    return '1 cuarto de kilómetro'
        if unit_distance > 1:
            unit = unit + 's'
        if len(fraction_text) > 0:
            if language == 'en_US':
                fraction_text = ' and ' + fraction_text
            else:
                fraction_text = ' y ' + fraction_text
        return str(int(unit_distance)) + fraction_text + ' ' + unit

    @staticmethod
    def site_response(site, date, language):
        day_of_week = date.strftime('%A')
        display_day = day_of_week
        if language == "es_US":
            display_day = Schedule.WEEKDAYS_ES.get(day_of_week)
        if day_of_week not in site.schedules.keys():
            raise Exception('Site is not open on this day')
        return {
            'site_id': site.id,
            'distance': FindPantryResource.readable_distance(site.distance, language),
            'site_name': site.name,
            'site_address': site.address,
            'site_city': site.city,
            'site_open': site.schedules.get(day_of_week).open_time.strftime('%I:%M %p'),
            'site_close': site.schedules.get(day_of_week).close_time.strftime('%I:%M %p'),
            'day_of_week': display_day
        }

    def get(self):
        google_api_key = os.environ.get("GOOGLE_API_TOKEN")
        pgclient = get_postgres_client()
        try:
            with pgclient:
                city = request.args.get("city")
                address = request.args.get("address")
                language = request.args.get("language", "en_US")
                try:
                    formatted_address = '{}, {}, {}'.format(address, city, 'CA')
                    gmaps = googlemaps.Client(key=google_api_key)
                    geocode = gmaps.geocode(formatted_address)
                    log.debug(str(geocode))
                    geolocation = geocode[0].get('geometry').get('location')
                except (ApiError, Timeout, TransportError) as e:
                    log.exception("Encountered an exception while geocoding the user's address")
                    return make_response("An error occurred", 500)

                dao = PostgresDistributionSiteDao(pgclient)

                today = datetime.datetime.now(tz=pytz.timezone("America/Los_Angeles")).date()
                tomorrow = today + datetime.timedelta(days=1)
                day_after = today + datetime.timedelta(days=2)

                sites_today = dao.find_open_sites_now(geolocation['lat'], geolocation['lng'])
                sites_tomorrow = dao.find_open_sites_on_day(geolocation['lat'], geolocation['lng'], tomorrow)
                sites_day_after = dao.find_open_sites_on_day(geolocation['lat'], geolocation['lng'], day_after)

                site_responses_today = [FindPantryResource.site_response(site_summary, today, language) for site_summary in sites_today]
                site_responses_tomorrow = [FindPantryResource.site_response(site_summary, tomorrow, language) for site_summary in sites_tomorrow]
                site_responses_day_after = [FindPantryResource.site_response(site_summary, day_after, language) for site_summary in sites_day_after]

                site_responses = {
                    "sites": site_responses_today + site_responses_tomorrow + site_responses_day_after
                }



                if len(site_responses) > 0:
                    return jsonify(site_responses)
                else:
                    return make_response("No sites were found", 404)
        except Exception as e:
            log.exception("Encountered an exception while finding a pantry")
            return make_response("An error occurred", 500)
        finally:
            pgclient.close()




