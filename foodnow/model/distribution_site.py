from datetime import datetime


class DistributionSite(object):

    def __init__(self, **kwargs):
        self.name = kwargs.get('Name', '')
        self.address = kwargs.get('Address', '')
        self.city = kwargs.get('City', '')
        self.zip = kwargs.get('ZipCode', '')
        self.open_date = datetime.strptime(kwargs.get('OpenDate'), '%Y-%m-%d')
        self.close_date = datetime.strptime(kwargs.get('CloseDate'), '%Y-%m-%d')
        self.days_of_week = [day.strip() for day in kwargs.get('DayOfWeek', '').split(',')]
        self.open_time = datetime.strptime(kwargs.get('StartTime'), '%I:%M %p')
        self.close_time = datetime.strptime(kwargs.get('EndTime'), '%I:%M %p')

    def __repr__(self):
        return "{}".format(self.name)

