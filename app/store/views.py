#!/usr/bin/env python3
"""
"""

from flask import Blueprint, render_template, current_app, make_response, url_for
from bson.objectid import ObjectId
from pprint import pformat

store = Blueprint('store', __name__)


@store.route('/images/<pid>/<file_name>')
def images(pid, file_name):
    product = current_app.db.Product.get_from_id(ObjectId(pid))
    with product.fs.get_last_version('images/{}'.format(file_name)) as f:
        response  = make_response(f.read())
    response.mimetype = 'image/jpeg'
    return response


@store.route('/product/<pid>')
@store.route('/product/<pid>/<product_name>')
def product(pid, product_name=None):
    product_id = ObjectId(pid)
    product = current_app.db.Product.get_from_id(product_id)
    categories = [c.category['name'] for c in current_app.db.ProductToCategory.find({'product._id': product_id})]
    return render_template('store/product.html', product=product, categories=pformat(categories, indent=4))

@store.route('/')
def store_front():
    popular = []
    while len(popular) < 4:
        product = current_app.db.Product.find_random()
        if product not in popular:
            popular.append(product)

    latest = [current_app.db.Product.find_random(),current_app.db.Product.find_random(),current_app.db.Product.find_random()]
    print(latest)

    return render_template('store/index.html', most_popular=popular, latest=latest)
