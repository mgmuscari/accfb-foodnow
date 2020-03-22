from flask import Flask
from flask_restful import Api
from foodnow.rest.root import RootResource
from foodnow.rest.find_pantry import FindPantryResource

app = Flask(__name__)
api = Api(app)

api.add_resource(RootResource, '/')
api.add_resource(FindPantryResource, '/find-pantry')


if __name__ == '__main__':
    app.run(debug=True)