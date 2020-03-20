from flask_restful import Resource
from flask import request


class DistributionSite(Resource):
    def post(self):
        print(request.json)