from foodnow.model.distribution_site import DistributionSite
from foodnow.db.postgres.schedule_dao import PostgresScheduleDao
import pytz
import datetime
import logging

log = logging.getLogger(__name__)

class PostgresDistributionSiteDao(object):

    def __init__(self, pg_client):
        self.pg_client = pg_client

    def get_site(self, id):
        schedule_dao = PostgresScheduleDao(self.pg_client)
        with self.pg_client.cursor() as cursor:
            cursor.execute(
                'select *, st_x(location::geometry) as lng, st_y(location::geometry) as lat from accfb.distribution_sites where id=%(id)s',
                {'id': id})
            result = cursor.fetchone()
            if result is not None:
                columns = [col.name for col in cursor.description]
                data = dict(zip(columns, result))
                site = DistributionSite(
                    **{
                        'ID': data.get('id'),
                        'Name': data.get('name'),
                        'Address': data.get('address'),
                        'City': data.get('city'),
                        'Zipcode': data.get('zip'),
                        'OpenDate': data.get('open_date'),
                        'CloseDate': data.get('close_date')
                    }
                )
                site.set_location(data['lat'], data['lng'])
                site.schedules = schedule_dao.get_site_schedules(site.id)
                return site
            else:
                return None

    def save_site(self, site):
        with self.pg_client.cursor() as cursor:
            insert_query = 'insert into accfb.distribution_sites (id, name, address, city, zip, open_date, close_date, location) ' + \
                           'values (%(id)s, %(name)s, %(address)s, %(city)s, %(zip)s, %(open_date)s, %(close_date)s, ' + \
                           'st_makepoint(%(lng)s, %(lat)s)) on conflict (id) do update set name=%(name)s, address=%(address)s, ' + \
                           'city=%(city)s, zip=%(zip)s, open_date=%(open_date)s, close_date=%(close_date)s, location=st_makepoint(%(lng)s, %(lat)s)'

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
            self.pg_client.commit()

    def find_open_sites_now(self, lat, lng, num_sites=3):
        now = datetime.datetime.now(tz=pytz.timezone("America/Los_Angeles"))
        open_at = now + datetime.timedelta(hours=1)
        return self.find_open_sites_on_day(lat, lng, now, at_hour=open_at.time(), num_sites=3)

    def find_open_sites_on_day(self, lat, lng, date, at_hour=None, num_sites=3):
        weekday = date.strftime('%A')
        select = 'select {} from accfb.distribution_sites as ds inner join accfb.hours as hrs on ds.id=hrs.site_id {} {} {} {}'
        fields = 'ds.id as ID, ds.name as Name, ds.address as Address, ds.city as City, ds.zip as Zip, st_x(ds.location::geometry) as Longitude, st_y(ds.location::geometry) as Latitude, ds.open_date as OpenDate, ds.close_date as CloseDate, st_distance(st_point(%(lng)s, %(lat)s)::geography, location) as distance'
        where = 'where ds.open_date <= %(today)s and ds.close_date > %(today)s and hrs.day = %(weekday)s'
        and_hours = ''
        if at_hour is not None:
            and_hours = 'and hrs.close_time > %(open_at)s'
        order = 'order by distance asc'
        limit = 'limit %(num_sites)s'
        query = select.format(fields, where, and_hours, order, limit)
        schedule_dao = PostgresScheduleDao(self.pg_client)
        with self.pg_client.cursor() as cursor:
            cursor = self.pg_client.cursor()
            select_bindings = {
                "lng": lng,
                "lat": lat,
                "today": date,
                "weekday": weekday,
                "open_at": at_hour,
                "num_sites": num_sites
            }
            cursor.execute(query, select_bindings)
            columns = [col.name for col in cursor.description]
            site_rows = cursor.fetchall()

            distribution_sites = []

            for site_row in site_rows:
                site_data = dict(zip(columns, site_row))
                ds = DistributionSite(**{
                    "ID": site_data.get("id"),
                    "Name": site_data.get("name"),
                    "Address": site_data.get("address"),
                    "City": site_data.get("city"),
                    "Zipcode": site_data.get("zip"),
                    "OpenDate": site_data.get("opendate"),
                    "CloseDate": site_data.get("closedate"),
                    "Latitude": site_data.get("latitude"),
                    "Longitude": site_data.get('longitude')
                })
                ds.distance = site_data.get('distance')
                ds.schedules = schedule_dao.get_site_schedules(ds.id)
                distribution_sites.append(ds)
            return distribution_sites
        return None
