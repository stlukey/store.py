
from flask import Blueprint, current_app, render_template
from .modules.products.models import Product, db

store = Blueprint('store', __name__)


@store.route('/')
def index():

    latest = list(Product.find(_sort=("datetime", 1)))[:3]
    popular = list(Product.find(_sort=("datetime", -1)))[:4]

    return render_template('index.html',
                           most_popular=popular,
                           latest=latest)
