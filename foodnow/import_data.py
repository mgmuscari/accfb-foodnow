from foodnow.db import get_postgres_client
from foodnow.model.distribution_site import DistributionSite
import smartsheet
import os
import googlemaps
import traceback
import sys

if __name__ == '__main__':
    postgres = get_postgres_client()
    google_api_key = os.environ.get("GOOGLE_API_TOKEN")
    smartsheet_api_key = os.environ.get("SMARTSHEET_ACCESS_TOKEN")
    smartsheet_sheet_id = os.environ.get("SMARTSHEET_SHEET_ID")

    smartsheet_client = smartsheet.Smartsheet(smartsheet_api_key)
    smartsheet_client.errors_as_exceptions(True)

    sheet = smartsheet_client.Sheets.get_sheet(smartsheet_sheet_id)

    distribution_sites = []

    gmaps = googlemaps.Client(key=google_api_key)

    for row in sheet.rows:
        try:
            data = {}
            for cell in row.cells:
                column_name = sheet.get_column(cell.column_id).title
                value = cell.value
                data[column_name] = value

            # the raw values of the id and zip code are unfortunately read as float
            data['ID'] = int(data['ID'])
            data['Zipcode'] = int(data['Zipcode'])

            site = DistributionSite(**data)

            cursor = postgres.cursor()

            cursor.execute('select *, st_x(location::geometry) as lng, st_y(location::geometry) as lat from accfb.distribution_sites where id=%(id)s', {'id': site.id})

            result = cursor.fetchone()
            address_changed = False

            if result is not None:
                print("Found an existing row for {}".format(site.name))
                columns = [col.name for col in cursor.description]
                data = dict(zip(columns, result))
                old_address = '{}, {}, {} {}'.format(data['address'], data['city'], 'CA', data['zip'])
                new_address = '{}, {}, {} {}'.format(site.address, site.city, 'CA', site.zip)
                site.set_location(data['lat'], data['lng'])
                address_changed = old_address != new_address
                if address_changed:
                    print("Address of {} has changed".format(site.name))

            if address_changed or result is None:
                geocode = gmaps.geocode('{}, {}, {} {}'.format(site.address, site.city, 'CA', site.zip))
                location = geocode[0].get('geometry').get('location')
                site.set_location(location.get('lat'), location.get('lng'))

            insert_query = 'insert into accfb.distribution_sites (id, name, address, city, zip, open_date, close_date, location) ' + \
                           'values (%(id)s, %(name)s, %(address)s, %(city)s, %(zip)s, %(open_date)s, %(close_date)s, ' + \
                           'st_makepoint(%(lng)s, %(lat)s)) on conflict do update set name=%(name)s, address=%(address)s, ' + \
                           'city=%(city)s, zip=%(zip)s, open_date=%(open_date)s, close_date=%(close_date)s, location=st_makepoint(%(lng)s, %(lat)s))'
            update = {
                'id': site.id,
                'name': site.name,
                'address': site.address,
                'city': site.city,
                'zip': site.zip,
                'open_date': site.open_date,
                'close_date': site.close_date,
                'lng': site.longitude,
                'lat': site.latitude
            }

            cursor.execute(insert_query, update)

            cursor.execute('delete from accfb.hours where site_id=%(site_id)s', {'site_id': site.id})

            for day in site.days_of_week:
                insert_query = 'insert into accfb.hours (site_id, day, open_time, close_time) values (%(site_id)s, %(day)s, %(open)s, %(close)s)'
                update = {'site_id': site.id, 'day': day, 'open': site.open_time, 'close': site.close_time}
                cursor.execute(insert_query, update)

            postgres.commit()

        except Exception as e:
            traceback.print_exc(file=sys.stdout)


