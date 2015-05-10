import urlparse
import urllib

def encodeURL(url):
    if url and not '://' in url and '.' in url:
        url = 'http://' + url

    parsed = urlparse.urlparse(url)
    
    reserved_characters = ':/?#[]@!$&\'()*+,;="'

    scheme = parsed.scheme
    netloc = parsed.netloc.encode('idna')
    path = urllib.quote_plus(parsed.path.encode('utf-8'), reserved_characters)
    params = parsed.params #urllib.quote_plus(parsed.params, '&=%')
    query = urllib.quote_plus(parsed.query.encode('utf-8'), reserved_characters)
    fragment = urllib.quote_plus(parsed.fragment.encode('utf-8'), reserved_characters)

    return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))

def decodeURLPath(path):
    return urllib.unquote_plus(path)

def isValidScheme(url, schemes=['http', 'https']):
    parsed = urlparse.urlparse(url)
    return parsed.scheme in schemes

