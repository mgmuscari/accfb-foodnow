from foodnow.db import get_postgres_client

from foodnow.db.postgres.referral_dao import PostgresReferralDao
import smartsheet
import os
import logging
import sys
import datetime
import pytz

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    log = logging.getLogger('foodnow')
    log.setLevel(logging.DEBUG)

    postgres = get_postgres_client()

    smartsheet_api_key = os.environ.get("SMARTSHEET_ACCESS_TOKEN")
    smartsheet_sheet_id = os.environ.get("SMARTSHEET_METRICS_SHEET_ID")

    smartsheet_client = smartsheet.Smartsheet(smartsheet_api_key)
    smartsheet_client.errors_as_exceptions(True)

    sheet = smartsheet_client.Sheets.get_sheet(smartsheet_sheet_id)

    distribution_sites = []


    postgres_referrals_dao = PostgresReferralDao(postgres)

    today = datetime.datetime.now(tz=pytz.timezone("America/Los_Angeles")).date()
    referrals = postgres_referrals_dao.get_referrals_on_date(today)

    for referral in referrals:
        print(referral)


