from flask_restful import Resource, request
from foodnow.db import get_postgres_client
from foodnow.db.postgres.distribution_site_dao import PostgresDistributionSiteDao
from foodnow.db.postgres.referral_dao import PostgresReferralDao
from foodnow.model.referral import Referral
from foodnow.util import truthy_string, translate_number_string
import datetime
import pytz
import re
from text_to_num import text2num


class RecordReferralResource(Resource):

    def post(self):
        pgclient = get_postgres_client()
        try:
            date = request.form.get('date')
            has_children = truthy_string(request.args.get("has_children", "no")[:5])
            channel = request.form.get('channel')
            count = request.form.get('count', '1')
            language = request.form.get('language', 'en_US')
            if re.fullmatch('[0-9]+', count) is not None:
                # Oh look, the user responded with number words or something
                # This will only work for english. Otherwise we default to 1
                # This is to avoid having to actually make a call to the google translate API just to parse some numbers
                count = translate_number_string(count)
            else:
                # thank god, the user gave us digits
                count = int(count)
            if date is not None:
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
            else:
                date = datetime.datetime.now(tz=pytz.timezone("America/Los_Angeles")).date()
            site_id = request.form.get('site_id', None)
            if site_id is not None:
                distribution_site_dao = PostgresDistributionSiteDao(pgclient)
                site = distribution_site_dao.get_site(site_id)
                if site is not None:
                    referral = Referral(site, date, count)
                    referral_dao = PostgresReferralDao(pgclient)
                    referral_dao.increment_referral(referral)
        finally:
            pgclient.close()
