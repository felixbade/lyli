import time
import json

from flask import session, request, g, flash

from app import app
import config

logfile = open(config.logfilename, 'a')

def log(dictionary):
    logfile.write(json.dumps(dictionary) + '\n')
    logfile.flush()



id_prefix = str(int(time.time()))
id_counter = 0
def get_new_id():
    global id_counter
    id_counter += 1
    return '%s-%d' % (id_prefix, id_counter)



@app.before_request
def before():
    # time() has to have sub-second resolution for this to work
    g.response_start_time = time.time()
    g.notes = {}

def shouldDeleteCookie(response):
    # Nothing to delete
    if not session:
        return False
    # Do Not Track
    if request.headers.get('Dnt') == '1':
        return True
    return False

def shouldSetCookie(response):
    # There is a cookie already
    if 'id' in session:
        return False
    # No cookie for users requesting Do Not Track.
    if request.headers.get('Dnt') == '1':
        return False
    # We should not put cookie if a new user just click's a short link
    # because she/he would have no way of knowing they are being tracked.
    # Or I don't know, for example bit.ly does exacly that any way.
    if response.status_code == 307:
        return False
    # No cookie for UptimeRobot.
    if request.method == 'HEAD':
        return False
    return True

@app.after_request
def after(response):
    if shouldSetCookie(response):
        session.permanent = True
        session['id'] = get_new_id()
    
    elif shouldDeleteCookie(response):
        session.clear()

    now = time.time()
    # Not including log write time, which might be significant.
    # We should probably do it on background.
    response_time = now - g.response_start_time

    data = {
            'timestamp' : now,
            'response-time': response_time,
            #'ip' : request.remote_addr, # always 127.0.0.1 because we are behind nginx
            'path': request.path,
            'args': dict(request.args),
            'method': request.method,
            'session': dict(session),
            'request-headers': dict(request.headers),
            'form': dict(request.form),
            'response-status': response.status_code,
            'response-headers': dict(response.headers), 
            'notes': g.notes
    }
    log(data)
    return response
