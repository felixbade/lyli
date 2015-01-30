from flask import request, render_template, redirect

from app import app
from app import request_logger
from app.urlshortener import URLShortener
from app.urlshortener.url import decodeURLPath, encodeURL, isValidScheme
from app.urlshortener.name import removeControlCharacters, isValidName

import config

backend = URLShortener()

def getDefaultName():
    name = request.form.get('default_name', '')
    return backend.getNextName(name)

def getIndexArgs():
    args = {}
    for key in ['default_name', 'name', 'url', 'brief']:
        args[key] = request.form.get(key, '')

    if request.method == 'POST':
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
            
            else:
                if args['brief'] == 'true':
                    success = backend.shorten(url, name, config.brief_ttl, 0)
                else:
                    success = backend.shorten(url, name, config.normal_ttl, config.normal_ttl)
                if success:
                    args['newurl'] = name
                    args['url'] = ''
                    args['name'] = ''
                else:
                    args['nameinuse'] = name

    return args

@app.route('/beta/', methods= ['GET', 'POST'])
@app.route('/beta/<name>', methods = ['GET', 'POST'])
def beta(name=''):
    try:
        args = getIndexArgs()
        code = 200
        if name != '':
            url = backend.visit(name)
            if url is None:
                args['nosuchname'] = name
                code = 404
            else:
                return redirect(url, code=307)
        args['default_name'] = getDefaultName()
        return render_template('index-beta.html', **args), code
    except:
        import traceback
        return str(traceback.format_exc())

@app.route('/ehdot/')
@app.route('/ehdot')
def terms():
    return render_template('terms.html')

@app.route('/', methods =['HEAD'])
def indexhead():
    return render_template('index.html')

@app.route('/', methods = ['GET', 'POST'])
@app.route('/<name>', methods = ['GET', 'POST'])
def index(name=''):
    args = getIndexArgs()
    code = 200
    if name != '':
        url = backend.visit(name)
        if url is None:
            args['nosuchname'] = name
            code = 404
        else:
            return redirect(url, code=307)
    
    args['default_name'] = getDefaultName()
    return render_template('index.html', **args), code

@app.errorhandler(404)
def notfound(error):
    return render_template('index.html',
            default_name = getDefaultName(),
            nosuchsite = request.path), 404

@app.errorhandler(500)
def internalerror(error):
    return render_template('500.html'), 500
