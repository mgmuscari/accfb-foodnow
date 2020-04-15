

class Referral(object):

    def __init__(self, site, date, channel, language, count):
        self.site = site
        self.date = date
        self.channel = channel
        self.language = language
        self.count = count

    def __repr__(self):
        return '({}) {}, {}, {}, {}: {}'.format(self.site.agency_number,
                                                self.site.name,
                                                self.language,
                                                self.channel,
                                                self.date,
                                                self.count)