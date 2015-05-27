from flask import Flask

import config

app = Flask(__name__)
app.secret_key = config.secret_key

from app.urlshortener import URLShortener

backend = URLShortener()

from app import views
from app import request_logger
