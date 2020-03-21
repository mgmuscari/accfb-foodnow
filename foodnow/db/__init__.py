import psycopg2
import os
from urllib import parse


def get_postgres_client():
    database_url = os.environ.get("DATABASE_URL")
    parsed = parse.urlparse(database_url)
    split = str(parsed.netloc).split('@')
    database = parsed.path[1:]
    auth = split[0]
    netloc = split[1]
    (user, passwd) = auth.split(':')
    (host, port) = netloc.split(':')
    return psycopg2.connect(host=host, port=port, user=user, password=passwd, database=database)

