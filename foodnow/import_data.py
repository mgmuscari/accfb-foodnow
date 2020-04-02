from foodnow.db import get_postgres_client

from foodnow.db.smartsheets.distribution_site_dao import SmartsheetDistributionSiteDao
from foodnow.db.postgres.distribution_site_dao import PostgresDistributionSiteDao
from foodnow.db.postgres.schedule_dao import PostgresScheduleDao
import smartsheet
import os
import googlemaps
import logging
import sys


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    log = logging.getLogger('foodnow')
    log.setLevel(logging.DEBUG)

    postgres = get_postgres_client()
    google_api_key = os.environ.get("GOOGLE_API_TOKEN")
    smartsheet_api_key = os.environ.get("SMARTSHEET_ACCESS_TOKEN")
    smartsheet_sheet_id = os.environ.get("SMARTSHEET_SHEET_ID")

    smartsheet_client = smartsheet.Smartsheet(smartsheet_api_key)
    smartsheet_client.errors_as_exceptions(True)

    sheet = smartsheet_client.Sheets.get_sheet(smartsheet_sheet_id)

    distribution_sites = []

    gmaps = googlemaps.Client(key=google_api_key)

    smartsheet_dao = SmartsheetDistributionSiteDao(sheet)
    postgres_site_dao = PostgresDistributionSiteDao(postgres)
    postgres_schedule_dao = PostgresScheduleDao(postgres)

    sites = smartsheet_dao.get_sites()

    try:
        for smartsheet_site in sites:
            log.debug("Loaded site from smartsheet: {}".format(str(smartsheet_site)))
            postgres_site = postgres_site_dao.get_site(smartsheet_site.id)
            address_changed = False
            if postgres_site is not None:
                log.debug("Loaded site from postgres: {}".format(str(postgres_site)))
                new_address = '{}, {}, {} {}'.format(smartsheet_site.address, smartsheet_site.city, 'CA', smartsheet_site.zip)
                old_address = '{}, {}, {} {}'.format(postgres_site.address, postgres_site.city, 'CA', postgres_site.zip)
                address_changed = old_address != new_address
                if address_changed:
                    log.debug("Address of {} has changed".format(smartsheet_site.name))

            if address_changed or postgres_site is None:
                log.debug("Geocoding site: {}".format(smartsheet_site.name))
                geocode = gmaps.geocode('{}, {}, {} {}'.format(smartsheet_site.address, smartsheet_site.city, 'CA', smartsheet_site.zip))
                location = geocode[0].get('geometry').get('location')
                smartsheet_site.set_location(location.get('lat'), location.get('lng'))
            else:
                smartsheet_site.set_location(postgres_site.latitude, postgres_site.longitude)

            log.debug("Saving site")
            postgres_site_dao.save_site(smartsheet_site)
            log.debug("Saving schedule")
            postgres_schedule_dao.save_site_schedules(smartsheet_site)
    except Exception as e:
        log.exception('An error occurred importing data')


