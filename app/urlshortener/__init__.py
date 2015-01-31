import redis

from app.urlshortener.name import getNthName
import config

class URLShortener:
    
    def __init__(self):
        self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.namespace = 'lyli'

    def shorten(self, url, name, begin_ttl, click_ttl):
        existing_url = self.get(name)
        if existing_url is None:
            self.r.set(self.getRedisKeyForURL(name), url)
            self.r.set(self.getRedisKeyForVisitCount(name), 0)
            self.setClickTTL(name, click_ttl)
            self.setTTL(name, begin_ttl)
            return True
        # TODO: what should happen if one is brief link and one is not?
        #elif existing_url == url:
        #    self.resetClickTTL(name)
        #    return True
        else:
            return False

    def visit(self, name):
        url = self.get(name)
        if url is not None:
            self.r.incr(self.getRedisKeyForVisitCount(name))
            self.resetClickTTL(name)
        return url

    def getNextName(self, name=None):
        if name and not self.exists(name):
            return name
        while True:
            n = self.getNextNameIndex()
            name = getNthName(n)
            if not self.exists(name):
                return unicode(name)
    
    def getNextNameIndex(self):
        n = self.r.incr(self.getRedisKeyForDefaultNameIndex())
        return n

    def resetNameIndex(self):
        self.r.set(self.getRedisKeyForDefaultNameIndex(), 0)



    def exists(self, name):
        url = self.get(name)
        return url is not None

    def get(self, name):
        name = name.lower()
        url = self.r.get(self.getRedisKeyForURL(name))
        return url

    def getVisitCount(self, name):
        return self.r.get(self.getRedisKeyForVisitCount(name))

    
    
    # TODO: ttl refers to two things here.
    # 1) the redis attribute, how soon the link will vanish
    # 2) how much should the redis ttl attribute be set at minimum when visited
    
    # set type 2 ttl
    def resetClickTTL(self, name):
        ttl = self.r.get(self.getRedisKeyForTTL(name))
        try:
            ttl = int(ttl)
        except TypeError:
            ttl = config.normal_ttl # type 2 minimum
        ttl = max(ttl, self.getTTL(name)) # don't decrement type 1
        self.setTTL(name, ttl)

    # set type 2 minimum ttl
    def setClickTTL(self, name, ttl):
        self.r.set(self.getRedisKeyForTTL(name), ttl)

    # return type 1 ttl
    def getTTL(self, name):
        return self.r.ttl(self.getRedisKeyForURL(name))

    # set type 1 ttl
    def setTTL(self, name, ttl):
        self.r.expire(self.getRedisKeyForURL(name), ttl)
        self.r.expire(self.getRedisKeyForTTL(name), ttl)
        self.r.expire(self.getRedisKeyForVisitCount(name), ttl)



    def getRedisKeyForURL(self, name):
        return self.getRedisKey('url', name)

    def getRedisKeyForVisitCount(self, name):
        return self.getRedisKey('visit-count', name)
    
    def getRedisKeyForTTL(self, name):
        return self.getRedisKey('ttl', name)

    def getRedisKeyForDefaultNameIndex(self):
        return self.getRedisKey('default-name-index')

    def getRedisKey(self, *args):
        return ':'.join((self.namespace,) + args)
