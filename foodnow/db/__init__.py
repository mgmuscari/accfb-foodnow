import redis
import os
from urllib import parse


def get_redis_client():
    redis_url = os.environ.get("REDIS_URL")
    parsed = parse.urlparse(redis_url)
    split = parsed.netloc.split('@')
    if len(split) == 2:
        auth = split[0]
        netloc = split[1]
        passwd = auth.split(':')[1]
        (host, port) = netloc.split(':')
    elif len(split) == 1:
        (host, port) = split[0].split(':')
        passwd = None
    r = redis.Redis(host, port, password=passwd)