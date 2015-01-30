import time
import json

from flask import session, request, g

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

@app.after_request
def after(response):
    # We should not put cookie if a new user just click's a short link
    # because she/he would have no way of knowing they are being tracked.
    # Or I don't know, for example bit.ly does exacly that any way.
    # Also, no cookie for UptimeRobot.
    if 'id' not in session and response.status_code != 307 and request.method != 'HEAD':
        session.permanent = True
        session['id'] = get_new_id()

    now = time.time()
    # Not including log write time, which might be significant.
    # We should probably do it on background.
    response_time = now - g.response_start_time

    data = {
            'timestamp' : now,
            'response-time': response_time,
            #'ip' : request.remote_addr, # always 127.0.0.1 because we are behind nginx
            'path': request.path,
            'method': request.method,
            'session': dict(session),
            'request-headers': dict(request.headers),
            'form': dict(request.form),
            'response-status': response.status_code,
            'response-headers': dict(response.headers)
    }
    log(data)
    return response
