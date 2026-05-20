import redis
import json
import os

class SessionMemory:
    def __init__(self):
        self.r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0
        )

    def get(self, session_id):
        val = self.r.get(session_id)
        if val:
            return json.loads(val)
        return {}

    def set(self, session_id, data, ttl=600):
        self.r.set(session_id, json.dumps(data), ex=ttl)

    def clear(self, session_id):
        self.r.delete(session_id)