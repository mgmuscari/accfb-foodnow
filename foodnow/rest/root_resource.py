from flask_restful import Resource
from foodnow.db import get_postgres_client


class RootResource(Resource):
    def get(self):
        return "boop"

