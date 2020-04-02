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
                if ValidCityResource.valid_city(pgclient, city):
                    return jsonify({"valid_city": True, "city": city})
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
        select = 'select * from accfb.cities where lower(name)=lower(%(city)s)'
        with pgclient.cursor() as cursor:
            cursor.execute(select, {'city': city})
            row = cursor.fetchone()
            return row is not None
        return False
