import redis

from app.urlshortener.name import getNthName

class URLShortener:
    
    def __init__(self):
        self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.namespace = 'shorturl'
        self.ttl = 60*60*24*7*2 # two weeks

    def shorten(self, url, name):
        existing_url = self.get(name)
        if existing_url is None:
            self.r.set(self.getRedisKeyForURL(name), url)
            self.r.set(self.getRedisKeyForVisitCount(name), 0)
            self.resetTTL(name)
            return True
        elif existing_url == url:
            self.resetTTL(name)
            return True
        else:
            return False

    def visit(self, name):
        url = self.get(name)
        if url is not None:
            self.r.incr(self.getRedisKeyForVisitCount(name))
            self.resetTTL(name)
        return url

    def getNextName(self, name=None):
        if name and not self.exists(name):
            return name
        while True:
            n = self.r.incr(self.getRedisKeyForDefaultNameIndex())
            name = getNthName(n)
            if not self.exists(name):
                return unicode(name)

    def resetNameIndex(self):
        self.r.set(self.getRedisKeyForDefaultNameIndex(), 0)



    def exists(self, name):
        url = self.get(name)
        return url is not None

    def get(self, name):
        return self.r.get(self.getRedisKeyForURL(name))

    def getVisitCount(self, name):
        return self.r.get(self.getRedisKeyForVisitCount(name))

    def resetTTL(self, name):
        self.r.expire(self.getRedisKeyForURL(name), self.ttl)
        self.r.expire(self.getRedisKeyForVisitCount(name), self.ttl)

    def getTTL(self, name):
        return self.r.ttl(self.getRedisKeyForURL(name))



    def getRedisKeyForURL(self, name):
        return self.getRedisKey('url', name)

    def getRedisKeyForVisitCount(self, name):
        return self.getRedisKey('visit-count', name)
    
    def getRedisKeyForDefaultNameIndex(self):
        return self.getRedisKey('default-name-index')

    def getRedisKey(self, *args):
        return ':'.join((self.namespace,) + args)
