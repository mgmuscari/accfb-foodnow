from flask import Flask
from flask_restful import Api
from foodnow.rest.root import Root
from foodnow.rest.distribution_site import DistributionSite

app = Flask(__name__)
api = Api(app)

api.add_resource(Root, '/')
api.add_resource(DistributionSite, '/distribution-site')


if __name__ == '__main__':
    app.run(debug=True)