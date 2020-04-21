from flask_restful import Resource
from flask import request, make_response
from flask import jsonify
from foodnow.db import get_postgres_client
import logging
from foodnow import nlp_en, nlp_es

class ValidCityResource(Resource):

    def get(self):
        try:
            city = request.args.get("city")
            language = request.args.get("language")

            pgclient = get_postgres_client()
            try:
                # fuzzy search for a city
                found_city = ValidCityResource.valid_city(pgclient, city)
                if found_city is not None:
                    return jsonify({"valid_city": True, "city": found_city})
                else:
                    # let's try again using NLP to extract the city
                    if language == "en_US":
                        parsed = nlp_en(city)
                    else:
                        parsed = nlp_es(city)
                    entities = parsed.ents
                    for entity in entities:
                        stripped = entity.string.lower().replace("california","").strip()
                        city = ValidCityResource.valid_city(pgclient, stripped)
                        if city is not None:
                            return jsonify({"valid_city": True, "city": city})
            finally:
                pgclient.close()
            return jsonify({"valid_city": False, "city": city})

        except Exception as e:
            logging.exception("An error occurred validating the user's city")
            return make_response("An error occurred", 500)

    @staticmethod
    def valid_city(pgclient, city):
        city = city.split(",")[0].strip()
        select = 'select name from accfb.cities where levenshtein(lower(%(city)s), lower(name)) < 3 order by levenshtein(lower(%(city)s), lower(name)) asc'
        with pgclient.cursor() as cursor:
            cursor.execute(select, {'city': city})
            row = cursor.fetchone()
            if row is not None:
                return row[0]
        return None
