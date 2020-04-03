from flask_restful import Resource, request
from foodnow.db import get_postgres_client
from foodnow.db.postgres.distribution_site_dao import PostgresDistributionSiteDao
from foodnow.db.postgres.referral_dao import PostgresReferralDao
from foodnow.model.referral import Referral
import datetime
import pytz


class RecordReferralResource(Resource):

    def post(self):
        pgclient = get_postgres_client()
        try:
            now = datetime.datetime.now(tz=pytz.timezone("America/Los_Angeles")).date()
            site_id = request.form.get('site_id', None)
            count = request.form.get('count', 1)
            if site_id is not None:
                distribution_site_dao = PostgresDistributionSiteDao(pgclient)
                site = distribution_site_dao.get_site(site_id)
                if site is not None:
                    referral = Referral(site, now, count)
                    referral_dao = PostgresReferralDao(pgclient)
                    referral_dao.increment_referral(referral)
        finally:
            pgclient.close()
