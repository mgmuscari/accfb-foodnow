from flask_restful import Resource
from foodnow.db import get_redis_client

class Root(Resource):
    def get(self):
        redis = get_redis_client()
        count = redis.incr('test_counter', 1)
        return {'Hit Counter': count}