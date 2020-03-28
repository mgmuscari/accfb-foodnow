from flask import Flask
from flask_restful import Api
from flask_restful import abort
from flask import request
from foodnow.rest.root import RootResource
from foodnow.rest.find_pantry import FindPantryResource
from foodnow.rest.valid_city import ValidCityResource
from twilio.request_validator import RequestValidator
import os
import logging

app = Flask(__name__)
api = Api(app)

api.add_resource(RootResource, '/')
api.add_resource(FindPantryResource, '/find-pantry')
api.add_resource(ValidCityResource, '/validate-city')

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.before_request
def verify_request():
    try:
        twilio_signature = request.headers['X-Twilio-Signature']
        twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        validator = RequestValidator(twilio_auth_token)
        auth = request.authorization
        user = None
        password = None
        if auth is not None:
            user = request.authorization.username
            password = request.authorization.password
        url = request.url
        content = request.form
        if not (validator.validate(url, content, twilio_signature) or (user == "debug" and password == twilio_auth_token)):
            abort(401)
    except Exception as e:
        logging.exception("Something went wrong", e)
        abort(401)

if __name__ == '__main__':
    app.run(debug=True)