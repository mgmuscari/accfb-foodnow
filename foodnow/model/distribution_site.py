from datetime import datetime, date

from foodnow.model.schedule import Schedule

class DistributionSite(object):

    def __init__(self, **kwargs):
        self.id = kwargs.get("ID")
        self.name = kwargs.get("Name")
        self.address = kwargs.get("Address")
        self.city = kwargs.get("City")
        self.zip = kwargs.get("Zipcode")
        self.schedules = None
        if isinstance(kwargs.get("OpenDate"), date):
            self.open_date = kwargs.get("OpenDate")
        else:
            self.open_date = datetime.strptime(kwargs.get("OpenDate"), '%Y-%m-%d')
        if isinstance(kwargs.get("CloseDate"), date):
            self.close_date = kwargs.get("CloseDate")
        else:
            self.close_date = datetime.strptime(kwargs.get("CloseDate"), '%Y-%m-%d')
        self.latitude = kwargs.get("Latitude")
        self.longitude = kwargs.get("Longitude")

    def set_schedules_from_database(self, schedule_rows):
        self.schedules = {row.get('day'): Schedule(day_of_week=row.get('day'),
                                   open_time=row.get('open_time'),
                                   close_time=row.get('close_time')) for row in schedule_rows}

    def set_schedules_from_spreadsheet(self, **kwargs):
        days_of_week = [day.strip() for day in kwargs.get('DayOfWeek', '').split(',')]
        open_time = datetime.strptime(kwargs.get('StartTime'), '%I:%M %p')
        close_time = datetime.strptime(kwargs.get('EndTime'), '%I:%M %p')
        self.schedules = {day: Schedule(day_of_week=day, open_time=open_time, close_time=close_time) for day in days_of_week}

    def key(self):
        return "distribution_site:{}".format(self.id)

    def set_location(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return "{}: {}, {}, {}, {}. Open: {}".format(self.id, self.name, self.address, self.city, self.zip, self.schedules)

