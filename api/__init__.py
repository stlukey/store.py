#!/usr/bin/env python
"""
Main application.
"""

import os

from flask import Flask, Blueprint, url_for
import appenlight_client.ext.flask as appenlight

from .resources import register_resources
from .admin_resources import register_resources as register_admin_resources
from .utils import ObjectIDConverter


app = Flask(__name__)
app.config.update(
    DEBUG=bool(int(os.environ['FLASK_DEBUG'])),
    TESTING=bool(int(os.environ['FLASK_TESTING'])),
    SECRET_KEY=os.environ['FLASK_SECRET']
)
app.url_map.converters['ObjectID'] = ObjectIDConverter

if os.environ['APPENLIGHT_API_KEY']:
    app = appenlight.add_appenlight(app, 
        {'appenlight.api_key':os.environ['APPENLIGHT_API_KEY']})

admin = Blueprint('api', __name__, url_prefix='/admin')

register_resources(app)
register_admin_resources(admin)

app.register_blueprint(admin)

@app.route('/')
def root():
    return url_for('api.productsadmin')

@app.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origin"] = os.environ['JS_ORIGIN']
    response.headers["Access-Control-Allow-Credentials"] = 'true'
    response.headers["Access-Control-Allow-Methods"] = 'GET, POST, PUT, DELETE'
    response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept"
    return response


def main():
    app.run(threaded=True) 


if __name__ == '__main__':
    main()
