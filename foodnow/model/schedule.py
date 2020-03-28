class Schedule(object):

    def __init__(self, **kwargs):
        self.day_of_week = kwargs.get('day_of_week')
        self.open_time = kwargs.get('open_time')
        self.close_time = kwargs.get('close_time')

    def __repr__(self):
        return "[{}: {} - {}]".format(self.day_of_week, self.open_time, self.close_time)