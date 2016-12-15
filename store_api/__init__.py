#!/usr/bin/env python
"""
Main application.
"""

import os

from flask import Flask
from flask_httpauth import HTTPBasicAuth

from .resources import register_resources
from .utils import ObjectIDConverter


app = Flask(__name__)
app.config.update(
    DEBUG=bool(int(os.environ['FLASK_DEBUG'])),
    TESTING=bool(int(os.environ['FLASK_TESTING'])),
    SECRET_KEY=os.environ['FLASK_SECRET']
)

app.url_map.converters['ObjectID'] = ObjectIDConverter
register_resources(app)

def main():
    app.run()

if __name__ == '__main__':
    main()

