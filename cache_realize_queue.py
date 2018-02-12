# /usr/bin/python2
# -*- coding:utf8 -*-
import redis
import time
import json


class FakeQueue(object):
    def __init__(self, cache=None):
        self.cache = cache
        self.qname = 'queue_name'
        self.qdata_name = 'what_data'

    def push(self, record_id, delay_second=0, count=1):
        ts = int(time.time())
        data = {"id": record_id, "count": count}

        self.cache.hset(self.qdata_name, record_id, json.dumps(data))
        self.cache.zadd(self.qname, record_id, int(ts + delay_second))

    def pop(self, count=1):
        data = []
        score = int(time.time())
        order_ids = self.cache.zrangebyscore(self.qname, 0, score, start=0, num=count)
        if order_ids:
            order_ids = list(set(order_ids))
            pipe = self.cache.pipeline()
            for order_id in order_ids:
                pipe.zrem(self.qname, order_id)
            order_ids = [order_id for order_id, flag in zip(order_ids, pipe.execute()) if flag]
            if order_ids:
                for item in self.cache.hmget(self.qdata_name, *order_ids):
                    print(item)
                data = [json.loads(item) for item in self.cache.hmget(self.qdata_name, *order_ids)]
                self.cache.hdel(self.qdata_name, *order_ids)
        return data


redis_cfg = {
    'host': '127.0.0.1',
    'port': 6379,
    'password': 'Abcd1234!@#$'
}


def init_cache():
    _redis_pool = redis.ConnectionPool(**redis_cfg)
    return redis.Redis(connection_pool=_redis_pool)


cache = init_cache()
q = FakeQueue(cache=cache)
task_id = 1
q.push(record_id=task_id, delay_second=30)
q.pop()
