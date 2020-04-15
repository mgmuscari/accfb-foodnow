from datetime import datetime
from foodnow.model.schedule import Schedule
from foodnow.model.distribution_site import DistributionSite
import logging

log = logging.getLogger(__name__)

class SmartsheetDistributionSiteDao(object):

    def __init__(self, sheet):
        self.sheet = sheet

    def get_sites(self):
        sites = []
        columns = {}
        for column in self.sheet.columns:
            columns[column.id_] = column.title
        for row in self.sheet.rows:
            sites.append(self.get_site_from_row(row, columns))
        return sites

    def get_site_from_row(self, row, columns):
        try:
            data = {}
            for cell in row.cells:
                column_name = columns.get(cell.column_id)
                value = cell.value
                data[column_name] = value

            # the raw values of the id and zip code are unfortunately read as float
            data['Zipcode'] = int(data['Zipcode'])
            data['RequiresChildren'] = True if data['RequiresChildren'] is not None else False
            data['IsDrivethru'] = True if data['IsDrivethru'] is not None else False

            site = DistributionSite(**data)

            self.set_schedules(site, data['StartTime'], data['EndTime'], data['DayOfWeek'])
            return site
        except Exception as e:
            log.exception('An exception occurred reading a row')

    def set_schedules(self, site, open_time, close_time, schedule):
        days_of_week = [day.strip() for day in schedule.split(',')]
        open_time = datetime.strptime(open_time, '%I:%M %p')
        close_time = datetime.strptime(close_time, '%I:%M %p')
        site.schedules = {day: Schedule(day_of_week=day, open_time=open_time, close_time=close_time) for day in days_of_week}
