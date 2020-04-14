from foodnow.db.postgres.distribution_site_dao import PostgresDistributionSiteDao
from foodnow.model.referral import Referral


class PostgresReferralDao(object):

    def __init__(self, pg_client):
        self.pg_client = pg_client

    def increment_referral(self, referral):
        insert = 'insert into accfb.referrals (site_id, referral_date, channel, language, referrals) ' \
                 'values (%(site_id)s, %(channel)s, %(language)s, %(referral_date)s, %(count)s) {}'
        conflict = 'on conflict (site_id, referral_date) do update set referrals=accfb.referrals.referrals + %(count)s'
        upsert = insert.format(conflict)
        with self.pg_client.cursor() as cursor:
            cursor.execute(upsert, {'site_id': referral.site.id,
                                    'referral_date': referral.date,
                                    'channel': referral.channel,
                                    'language': referral.language,
                                    'count': referral.count})
        self.pg_client.commit()

    def get_referral(self, site, channel, language, date):
        select = 'select * from accfb.referrals where site_id=%(site_id)s and referral_date=%(date)s and channel=%(channel)s ' \
                 'and language=%(language)s'
        with self.pg_client.cursor() as cursor:
            cursor.execute(select, {'site_id': site.id, 'date': date, 'channel': channel, 'language': language})
            columns = [col.name for col in cursor.description]
            row = cursor.fetchone()
            if row is not None:
                result = dict(zip(columns, row))
                distribution_site_dao = PostgresDistributionSiteDao(self.pg_client)
                site = distribution_site_dao.get_site(result.get('site_id'))
                if site is not None:
                    return Referral(site, row.get('referral_date'), row.get('referrals'))
        return None

    def get_referrals_on_date(self, date):
        select = 'select * from accfb.referrals where referral_date=%(date)s'
        referrals = []
        with self.pg_client.cursor() as cursor:
            cursor.execute(select, {'date': date})
            columns = [col.name for col in cursor.description]
            rows = cursor.fetchall()
            distribution_site_dao = PostgresDistributionSiteDao(self.pg_client)
            for row in rows:
                result = dict(zip(columns, row))
                site = distribution_site_dao.get_site(result.get('site_id'))
                if site is not None:
                    referrals.append(Referral(site, row.get('referral_date'), row.get('referrals')))
        return referrals



