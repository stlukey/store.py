#!/usr/bin/env python
"""
Main application.
"""

from flask import Flask
from flask_login import LoginManager

from .models import init_db_docs
from .utils import ObjectIDConverter

from .modules.users.user import load_user
from .modules.products.queries import categories_get_all



class GlobalTemplateVars(object):
    categories = property(categories_get_all)



def create_app(config=None):
    if config is None:
        config = 'development'
    print("Using '{}' config.".format(config))
    config = '../configs/{}.cfg'.format(config)


    app = Flask(__name__)
    app.config.from_pyfile(config)

    app.add_template_global(GlobalTemplateVars(), 'global_vars')
    app.url_map.converters['ObjectID'] = ObjectIDConverter
    app.secret_key = app.config['SECRET']

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(load_user)

    register_blueprints(app)
    setup_mongodb(app)



    return app


def setup_mongodb(app):
    from mongokit import Connection

    app.db = Connection(app.config['MONGODB_URI'])

    init_db_docs(app)


def register_blueprints(app):
    from .views import store as store_bp
    from .modules.products import products_bp
    from .modules.users import users_bp
    from .modules.api import api_bp

    app.register_blueprint(store_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(users_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
