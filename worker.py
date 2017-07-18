import os
import redis
import urllib.parse
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
# urllib.parse.uses_netloc.append('redis')
#
# url = urllib.parse.urlparse(redis_url)
# conn = Redis(host=url.hostname, port=33507, db=0, password=url.password)
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
