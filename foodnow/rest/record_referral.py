from flask_restful import Resource
from foodnow.db import get_postgres_client


class RecordReferralResource(Resource):

    def post(self):
        pgclient = get_postgres_client()
        try:
            with pgclient:
                pass

        finally:
            pgclient.close()