#!/usr/bin/env python
"""
Main application.
"""

import os

from flask import Flask
from flask_login import LoginManager

from .modules.users.models import User
from .modules.products.models import Category
from .utils import ObjectIDConverter

from .views import store as store_bp
from .modules.products import products_bp
from .modules.users import users_bp
from .modules.api import api_bp


class GlobalTemplateVars(object):
    #TODO: Fix.
    categories = list(Category.find())

print(GlobalTemplateVars.categories)

app = Flask(__name__)
app.config.update(
    DEBUG=bool(int(os.environ.get('FLASK_DEBUG', False))),
    TESTING=bool(int(os.environ.get('FLASK_TESTING', False))),
    SECRET_KEY=os.environ.get('FLASK_SECRET', 'super secret')
)

app.add_template_global(GlobalTemplateVars(), 'global_vars')
app.url_map.converters['ObjectID'] = ObjectIDConverter

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.user_loader(User)


app.register_blueprint(store_bp)
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(users_bp)
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run()