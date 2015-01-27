#!flask/bin/python
import logging
from os import fork

import werkzeug.serving

from app import app

pid = fork()
if pid > 0:
    print('PID: %d' % pid)
    exit(0)
elif pid < 0:
    print('Could not fork: %d' % pid)
    exit(1)

# we are behind a proxy. log the ip of the end-user, not the proxy.
# this will also work without the proxy
werkzeug.serving.WSGIRequestHandler.address_string = lambda self: self.headers.get('x-real-ip', self.client_address[0])

# log to a file (access.log), not stderr
logging.basicConfig(filename='access.log', level=logging.DEBUG, format='%(message)s')

app.run(port=3004, debug=False, use_reloader=False)
