from urllib.parse import urlparse, urlunparse, quote_plus, unquote_plus

def encodeURL(url):
    url = url.strip(' ')
    
    if url and '://' not in url and '.' in url:
        url = 'http://' + url

    parsed = urlparse(url)
    
    reserved_characters = ':/?#[]@!$&\'()*+,;="%'

    scheme = parsed.scheme
    netloc = parsed.netloc.encode('idna').decode()
    path = quote_plus(parsed.path, reserved_characters)
    params = parsed.params
    query = quote_plus(parsed.query, reserved_characters)
    fragment = quote_plus(parsed.fragment, reserved_characters)

    return urlunparse((scheme, netloc, path, params, query, fragment))

def decodeURLPath(path):
    return unquote_plus(path)
