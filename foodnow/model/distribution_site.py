from datetime import datetime, date


class DistributionSite(object):

    def __init__(self, **kwargs):
        self.agency_number = kwargs.get("AgencyNo")
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
        self.requires_children = kwargs.get("RequiresChildren")
        self.is_drivethru = kwargs.get("IsDrivethru")
        self.latitude = kwargs.get("Latitude")
        self.longitude = kwargs.get("Longitude")
        self.distance = None

    def key(self):
        return "distribution_site:{}".format(self.id)

    def set_location(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return "{}: {}, {}, {}, {}. Open: {}".format(self.agency_number, self.name, self.address, self.city, self.zip, self.schedules)

