#!/usr/bin/env python
"""
Main application.
"""

import os
import logging
import sys

from flask import Flask, Blueprint, url_for, request
import appenlight_client.ext.flask as appenlight

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config.from_pyfile('config.py')


app.jinja_env.globals['JS_ORIGIN'] = app.config.get('JS_ORIGIN')

def set_access_control(response):
    response.headers["Access-Control-Allow-Origin"] = os.environ['JS_ORIGIN']
    response.headers["Access-Control-Allow-Credentials"] = 'true'
    response.headers["Access-Control-Allow-Methods"] = 'GET, POST, PUT, DELETE'
    response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
    return response

app.after_request(set_access_control)

@app.before_request
def before():
    if request.method == 'OPTIONS':
        return 'OK', 200



if os.environ['APPENLIGHT_API_KEY']:
    app = appenlight.add_appenlight(app,
        {'appenlight.api_key': os.environ['APPENLIGHT_API_KEY']})


from .utils import ObjectIDConverter
app.url_map.converters['ObjectID'] = ObjectIDConverter

admin = Blueprint('admin', __name__, url_prefix='/admin')

from .resources import register_resources
from .admin_resources import register_resources as register_admin_resources
register_resources(app)
register_admin_resources(admin)

app.register_blueprint(admin)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

def main():
    app.run(threaded=True)


if __name__ == '__main__':
    main()
