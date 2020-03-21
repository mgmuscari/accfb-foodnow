from flask import Flask
from flask_restful import Api
from foodnow.rest.root_resource import RootResource
from foodnow.rest.distribution_site_resource import DistributionSiteResource

app = Flask(__name__)
api = Api(app)

api.add_resource(RootResource, '/')
api.add_resource(DistributionSiteResource, '/distribution-site')


if __name__ == '__main__':
    app.run(debug=True)