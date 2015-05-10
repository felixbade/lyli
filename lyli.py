#!flask/bin/python
import logging

import werkzeug.serving

from app import app
import config

# we are behind a proxy. log the ip of the end-user, not the proxy.
# this will also work without the proxy
werkzeug.serving.WSGIRequestHandler.address_string = lambda self: self.headers.get('x-real-ip', self.client_address[0])

# log to a file (access.log), not stderr
logging.basicConfig(filename='access.log', level=logging.DEBUG, format='%(message)s')

if config.debug:
    app.run(port=3003, debug=True, use_reloader=True)
else:
    app.run(port=3004, debug=False, use_reloader=False)
