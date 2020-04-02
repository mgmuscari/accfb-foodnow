from flask import Flask
from flask_restful import Api
from flask_restful import abort
from flask import request, current_app
from foodnow.rest.find_pantry import FindPantryResource
from foodnow.rest.validate_city import ValidCityResource
from foodnow.rest.record_referral import RecordReferralResource
from twilio.request_validator import RequestValidator
import os
import logging

app = Flask(__name__, instance_relative_config=True)
api = Api(app)

api.add_resource(RecordReferralResource, '/record-referral')
api.add_resource(FindPantryResource, '/find-pantry')
api.add_resource(ValidCityResource, '/validate-city')

app_logger = app.logger
debug = os.environ.get('DEBUG', 'False')
auth = os.environ.get('AUTH', 'True')
if debug == 'True':
    logging.root.setLevel(logging.DEBUG)
    app_logger.setLevel(logging.DEBUG)

if auth == 'False':
    app.config['AUTH'] = False
else:
    app.config['AUTH'] = True

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.before_request
def verify_request():
    if current_app.config['AUTH']:
        try:
            twilio_signature = request.headers['X-Twilio-Signature']
            twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            validator = RequestValidator(twilio_auth_token)
            url = request.url
            content = request.form
            if not validator.validate(url, content, twilio_signature):
                abort(401)
        except Exception as e:
            logging.exception("Something went wrong")
            abort(401)


if __name__ == '__main__':
    app.run()

