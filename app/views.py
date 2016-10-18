# -*- coding: utf-8 -*-

from flask import request, render_template, redirect, g

from app import app
from app import backend
from app.email import get_email
from app.forms import ShorteningForm
from app.request_logger import seems_like_a_bot

import config

@app.route('/', methods=['POST'])
def shorten(complicated=False):
    form = ShorteningForm(request.form)
    if form.validate():
        g.notes['shortening'] = 'success'
        name = form.name.data or request.form.get('default_name', '')
        url = form.url.data
        duration = form.duration.data
        description = u'Lyhyt linkki vapautuu '
        passcode = None
        if duration == 'brief':
            passcode = backend.shorten(url, name, config.brief_ttl, 0)
            description += u'tunnin päästä, käytettiin sitä tai ei.'
        elif duration == 'once':
            passcode = backend.shorten(url, name, -1, 0)
            description += u'ensimmäisen avauksen jälkeen.'
        else:
            passcode = backend.shorten(url, name, config.normal_ttl, config.normal_ttl)
            description += u'kun sitä ei ole käytetty kolmeen viikkoon.'
        return frontpage(newurl=name, complicated=complicated, description=description, passcode=passcode)
    else:
        return frontpage(form=form, complicated=complicated)

@app.route('/monimutkainen/', methods=['POST'])
def complicated_shorten():
    return shorten(complicated=True)

@app.route('/')
def index():
    return frontpage()

@app.route('/monimutkainen/')
def complicated():
    return frontpage(complicated=True)

@app.route('/<name>')
def visit(name):
    url = backend.visit(name, seems_like_a_bot())
    if url:
        return redirect(url, code=307)
    else:
        return frontpage(nosuchlink=name, default_name=name, code=404)

@app.route('/poista-lyhennys/<name>/<passcode>')
def remove(name, passcode):
    if backend.delete(name, passcode):
        return frontpage(removedlink=name)
    elif backend.exists(name):
        return frontpage(didnotremovelink=name, code=403)
    else:
        return frontpage(nosuchlink=name, code=404)

@app.errorhandler(404)
def notfound(error):
    return frontpage(nosuchpage=request.path, code=404)

def frontpage(code=200, form=None, default_name=None, **args):
    if form is None:
        form = ShorteningForm()
    if default_name is None:
        default_name = getDefaultName()
    return render_template('index.html', form=form, default_name=default_name, email=get_email(), **args), code

def getDefaultName():
    name = request.form.get('default_name', '')
    default_name = backend.getNextName(name)
    g.notes['default_name'] = default_name
    return default_name

@app.route('/ehdot/')
def terms():
    return render_template('terms.html', email=get_email())

@app.route('/500.html')
def errorpage500():
    return render_template('500.html')
