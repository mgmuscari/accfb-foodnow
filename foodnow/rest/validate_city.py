from flask_restful import Resource
from flask import request, app, make_response
from flask import jsonify
from foodnow.db import get_postgres_client
import logging

log = logging.getLogger(__name__)


class ValidCityResource(Resource):

    def get(self):
        try:
            city = request.args.get("city")
            pgclient = get_postgres_client()
            try:
                found_city = ValidCityResource.valid_city(pgclient, city)
                if found_city is not None:
                    return jsonify({"valid_city": True, "city": found_city})
                else:
                    return jsonify({"valid_city": False, "city": city})
            finally:
                pgclient.close()

        except Exception as e:
            log.exception("An error occurred validating the user's city")
            return make_response("An error occurred", 500)

    @staticmethod
    def valid_city(pgclient, city):
        city = city.strip()
        select = 'select name from accfb.cities where levenshtein(lower(%(city)s), lower(name)) < 3 order by levenshtein(lower(%(city)s), lower(name)) asc'
        with pgclient.cursor() as cursor:
            cursor.execute(select, {'city': city})
            row = cursor.fetchone()
            if row is not None:
                return row[0]
        return None
