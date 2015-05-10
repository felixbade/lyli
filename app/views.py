from flask import request, render_template, redirect, g

from app import app
from app.urlshortener import URLShortener
from app.urlshortener.url import decodeURLPath, encodeURL, isValidScheme
from app.urlshortener.name import removeControlCharacters, isValidName
from app.email import getEmail

import config

backend = URLShortener()

def getDefaultName():
    name = request.form.get('default_name', '')
    return backend.getNextName(name)

def getIndexArgs():
    args = {}

    email = getEmail()
    args['email'] = email
    g.notes['email'] = email

    for key in ['default_name', 'name', 'url', 'brief', 'duration']:
        args[key] = request.form.get(key, '')

    if request.method == 'POST':
        url = args['url']
        try:
            url = encodeURL(url)
        except:
            args['illegalurl'] = True
            g.notes['shortening'] = 'illegal url'
        else:
            name = args['name'] or args['default_name']
            name = decodeURLPath(name)
            # This breaks emoji :(
            #name = removeControlCharacters(name)
            
            if url == '':
                args['emptyurl'] = True
                g.notes['shortening'] = 'empty url'
            
            elif not isValidScheme(url):
                args['illegalscheme'] = True
                g.notes['shortening'] = 'illegal scheme'
            
            elif not isValidName(name):
                args['illegalname'] = True
                g.notes['shortening'] = 'illegal name'
            
            else:
                if args['brief'] == 'true' or args['duration'] == 'brief':
                    success = backend.shorten(url, name, config.brief_ttl, 0)
                elif args['duration'] == 'once':
                    success = backend.shorten(url, name, -1, 0)
                else:
                    success = backend.shorten(url, name, config.normal_ttl, config.normal_ttl)
                if success:
                    g.notes['shortening'] = 'success'
                    args['newurl'] = name
                    args['url'] = ''
                    args['name'] = ''
                else:
                    g.notes['shortening'] = 'name in use'
                    args['nameinuse'] = name

    return args

@app.route('/beta/', methods= ['GET', 'POST'])
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
        default_name = getDefaultName()
        args['default_name'] = default_name
        g.notes['default_name'] = default_name
        return render_template('index-beta.html', **args), code
    except:
        import traceback
        return str(traceback.format_exc())

@app.route('/ehdot/')
@app.route('/ehdot')
def terms():
    args = getIndexArgs()
    return render_template('terms.html', **args)

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
    
    default_name = getDefaultName()
    args['default_name'] = default_name
    g.notes['default_name'] = default_name
    return render_template('index.html', **args), code

@app.route('/monimutkainen/', methods = ['GET', 'POST'])
def complicated():
    args = getIndexArgs()
    code = 200
    default_name = getDefaultName()
    args['default_name'] = default_name
    g.notes['default_name'] = default_name
    return render_template('monimutkainen.html', **args), code

@app.errorhandler(404)
def notfound(error):
    return render_template('index.html',
            default_name = getDefaultName(),
            nosuchsite = request.path), 404

@app.route('/500.html')
def errorpage500():
    return render_template('500.html')

@app.route('/e502.html')
def errorpage502():
    return render_template('502.html')
