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
import re


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
            'day_of_week': display_day,
            'date_open': date.strftime('%y-%m-%d'),
            'is_drivethru': site.is_drivethru,
            'requires_children': site.requires_children
        }

    @staticmethod
    def find_geocodes_in_city(geocode_results, city):
        filtered_results = []
        for result in geocode_results:
            locality_ac = next(filter(lambda ac: 'locality' in ac['types'], result['address_components']), None)
            if locality_ac is not None and locality_ac['long_name'].lower() == city.lower():
                filtered_results.append(result)
        return filtered_results

    @staticmethod
    def parse_has_children(value):
        return re.search('(s(i|í)|y(es)?)', value) is not None

    def get(self):
        google_api_key = os.environ.get("GOOGLE_API_TOKEN")
        pgclient = get_postgres_client()
        try:
            with pgclient:
                city = request.args.get("city")[:32]
                address = request.args.get("address")[:128]
                language = request.args.get("language", "en_US")[:5]
                has_children = FindPantryResource.parse_has_children(request.args.get("has_children", "no")[:5])
                try:
                    formatted_address = '{}, {}, {}'.format(address, city, 'CA')
                    gmaps = googlemaps.Client(key=google_api_key)
                    geocode_results = gmaps.geocode(formatted_address, components={'locality': city})
                    filtered_results = FindPantryResource.find_geocodes_in_city(geocode_results, city)
                    geocode = filtered_results[0]
                    logging.debug(str(geocode))
                    geolocation = geocode.get('geometry').get('location')
                except (ApiError, Timeout, TransportError) as e:
                    logging.exception("Encountered an exception while geocoding the user's address")
                    return make_response("An error occurred", 500)

                distribution_site_dao = PostgresDistributionSiteDao(pgclient)
                today = datetime.datetime.now(tz=pytz.timezone("America/Los_Angeles")).date()
                tomorrow = today + datetime.timedelta(days=1)
                day_after = today + datetime.timedelta(days=2)
                three_days = today + datetime.timedelta(days=3)

                sites_today = distribution_site_dao.find_open_sites_now(geolocation['lat'], geolocation['lng'], has_children=has_children)
                sites_tomorrow = distribution_site_dao.find_open_sites_on_day(geolocation['lat'], geolocation['lng'], tomorrow, has_children=has_children)
                sites_day_after = distribution_site_dao.find_open_sites_on_day(geolocation['lat'], geolocation['lng'], day_after, has_children=has_children)
                sites_three_days = distribution_site_dao.find_open_sites_on_day(geolocation['lat'], geolocation['lng'], three_days, has_children=has_children)

                site_responses_today = [FindPantryResource.site_response(site_summary, today, language) for site_summary in sites_today]
                site_responses_tomorrow = [FindPantryResource.site_response(site_summary, tomorrow, language) for site_summary in sites_tomorrow]
                site_responses_day_after = [FindPantryResource.site_response(site_summary, day_after, language) for site_summary in sites_day_after]
                site_responses_three_days = [FindPantryResource.site_response(site_summary, three_days, language) for
                                            site_summary in sites_three_days]

                site_responses = {
                    "sites": site_responses_today + site_responses_tomorrow + site_responses_day_after + site_responses_three_days
                }

                if len(site_responses) > 0:
                    return jsonify(site_responses)
                else:
                    return make_response("No sites were found", 404)
        except Exception as e:
            logging.exception("Encountered an exception while finding a pantry")
            return make_response("An error occurred", 500)
        finally:
            pgclient.close()




