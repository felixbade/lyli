from flask import request, render_template, redirect

from app import app
from app.urlshortener import URLShortener
from app.urlshortener.url import decodeURLPath, encodeURL, isValidScheme
from app.urlshortener.name import removeControlCharacters, isValidName

backend = URLShortener()

def getDefaultName():
    name = request.form.get('default_name', '')
    return backend.getNextName(name)

@app.route('/', methods = ['GET', 'POST'])
@app.route('/<name>', methods = ['GET', 'POST'])
def index(name=''):
    args = {}
    for key in ['default_name', 'name', 'url']:
        args[key] = request.form.get(key, '')

    if name != '':
        url = backend.visit(name)
        if url is None:
            args['nosuchname'] = name
        else:
            # TODO: add headers below
            # Cache-Control: no-cache
            # Pragma: no-cache
            return redirect(url, code=307)
    
    elif request.method == 'POST':
        url = args['url']
        try:
            url = encodeURL(url)
        except:
            args['illegalurl'] = True
        else:
            name = args['name'] or args['default_name']
            name = decodeURLPath(name)
            name = removeControlCharacters(name)
            
            if url == '':
                args['emptyurl'] = True
            
            elif not isValidScheme(url):
                args['illegalscheme'] = True
            
            elif not isValidName(name):
                args['illegalname'] = True
            
            elif backend.shorten(url, name):
                args['newurl'] = name
                args['url'] = ''
                args['name'] = ''
            else:
                args['nameinuse'] = name

    args['default_name'] = getDefaultName()
    return render_template('index.html', **args)

@app.errorhandler(404)
def notfound(error):
    return render_template('index.html',
            default_name = getDefaultName(),
            nosuchsite = request.path)

@app.errorhandler(500)
def notfound(error):
    return render_template('500.html')
