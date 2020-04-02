from foodnow.model.distribution_site import DistributionSite
import pytz
import datetime


class ReferralDao(object):

    def __init__(self, pg_client):
        self.pg_client = pg_client