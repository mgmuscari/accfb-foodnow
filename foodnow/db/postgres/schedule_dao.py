from foodnow.model.schedule import Schedule
import logging

log = logging.getLogger(__name__)

class PostgresScheduleDao(object):

    def __init__(self, pg_client):
        self.pg_client = pg_client

    def get_site_schedules(self, id):
        with self.pg_client.cursor() as cursor:
            select = 'select * from accfb.hours where site_id=%(id)s'
            cursor.execute(select, {'id': id})
            hour_columns = [col.name for col in cursor.description]
            hour_rows = cursor.fetchall()
            schedules = {}
            for row in hour_rows:
                row_dict = dict(zip(hour_columns, row))
                schedules[row_dict.get('day')] = Schedule(day_of_week=row_dict.get('day'),
                                                          open_time=row_dict.get('open_time'),
                                                          close_time=row_dict.get('close_time'))

            return schedules

    def save_site_schedules(self, site):
        with self.pg_client.cursor() as cursor:
            delete_query = 'delete from accfb.hours where site_id=%(site_id)s'
            cursor.execute(delete_query, {'site_id': site.id})
            for (day, schedule) in site.schedules.items():
                insert_query = 'insert into accfb.hours (site_id, day, open_time, close_time) values (%(site_id)s, %(day)s, %(open)s, %(close)s)'
                update = {'site_id': site.id, 'day': schedule.day_of_week, 'open': schedule.open_time,
                          'close': schedule.close_time}
                cursor.execute(insert_query, update)
            self.pg_client.commit()