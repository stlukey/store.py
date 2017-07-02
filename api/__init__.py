#!/usr/bin/env python
"""
Main application.
"""

import os

from flask import Flask, Blueprint, url_for
from flask_cors import CORS
import appenlight_client.ext.flask as appenlight


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config.from_pyfile('config.py')


app.jinja_env.globals['JS_ORIGIN'] = app.config.get('JS_ORIGIN')
cors = CORS(app, resources={r"/*": {"origins": app.config.get('JS_ORIGIN')}},
            supports_credentials=True)

if os.environ['APPENLIGHT_API_KEY']:
    app = appenlight.add_appenlight(app,
        {'appenlight.api_key':os.environ['APPENLIGHT_API_KEY']})


from .utils import ObjectIDConverter
app.url_map.converters['ObjectID'] = ObjectIDConverter

admin = Blueprint('api', __name__, url_prefix='/admin')

from .resources import register_resources
from .admin_resources import register_resources as register_admin_resources
register_resources(app)
register_admin_resources(admin)

app.register_blueprint(admin)

@app.route('/test')
def root():
    return "testing"

def main():
    app.run(threaded=True)


if __name__ == '__main__':
    main()
