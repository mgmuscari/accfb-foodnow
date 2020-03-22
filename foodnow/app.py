from flask import Flask
from flask_restful import Api
from foodnow.rest.root import RootResource
from foodnow.rest.find_pantry import FindPantryResource
from foodnow.rest.valid_city import ValidCityResource

app = Flask(__name__)
api = Api(app)

api.add_resource(RootResource, '/')
api.add_resource(FindPantryResource, '/find-pantry')
api.add_resource(ValidCityResource, '/validate-city')


if __name__ == '__main__':
    app.run(debug=True)