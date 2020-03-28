from foodnow.model.distribution_site import DistributionSite
import pytz
import datetime


class DistributionSiteDao(object):

    def __init__(self, pg_client):
        self.pg_client = pg_client

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
        cursor.close()

        distribution_sites = dict()

        for site_row in site_rows:
            site_data = dict(zip(columns, site_row))
            cursor = self.pg_client.cursor()
            select = 'select * from accfb.hours where site_id=%(id)s'
            cursor.execute(select, {'id': site_data.get('id')})
            hour_columns = [col.name for col in cursor.description]
            hour_rows = cursor.fetchall()
            schedules = [dict(zip(hour_columns, hour_row)) for hour_row in hour_rows]
            cursor.close()
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
            ds.set_schedules_from_database(schedules)
            distribution_sites[ds.id] = {"site": ds, "distance": site_data.get("distance")}
        return distribution_sites

