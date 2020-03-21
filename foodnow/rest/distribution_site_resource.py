from flask_restful import Resource
from flask import request
from foodnow.model.distribution_site import DistributionSite


class DistributionSiteResource(Resource):
    def post(self):
        print(DistributionSite(**request.json))

