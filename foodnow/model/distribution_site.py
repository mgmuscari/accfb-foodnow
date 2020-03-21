from datetime import datetime


class DistributionSite(object):

    def __init__(self, **kwargs):
        self.id = kwargs.get('ID')
        self.name = kwargs.get('Name', '')
        self.address = kwargs.get('Address', '')
        self.city = kwargs.get('City', '')
        self.zip = kwargs.get('Zipcode', '')
        self.open_date = datetime.strptime(kwargs.get('OpenDate'), '%Y-%m-%d')
        self.close_date = datetime.strptime(kwargs.get('CloseDate'), '%Y-%m-%d')
        self.days_of_week = [day.strip() for day in kwargs.get('DayOfWeek', '').split(',')]
        self.open_time = datetime.strptime(kwargs.get('StartTime'), '%I:%M %p')
        self.close_time = datetime.strptime(kwargs.get('EndTime'), '%I:%M %p')
        self.latitude = kwargs.get('Latitude', None)
        self.longitude = kwargs.get('Longitude', None)

    def key(self):
        return "distribution_site:{}".format(self.id)

    def set_location(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return "{}: {}, {}, {}, {}".format(self.id, self.name, self.address, self.city, self.zip)

