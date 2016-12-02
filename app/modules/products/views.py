#!/usr/bin/env python3
"""
"""

from flask import Blueprint, render_template, current_app, make_response
from bson.objectid import ObjectId

from . import queries

products = Blueprint('products', __name__)


@products.route('/<product_id>/images/<file_name>')
def images(product_id, file_name):
    product = current_app.db.Product.get_from_id(ObjectId(product_id))
    with product.fs.get_last_version('images/{}'.format(file_name)) as f:
        response = make_response(f.read())
    response.mimetype = 'image/jpeg'
    return response


@products.route('/<product_id>')
@products.route('/<product_id>/<product_name>')
def view_product(product_id, product_name=None):
    product_id = ObjectId(product_id)
    product = current_app.db.Product.get_from_id(product_id)
    categories = queries.product_find_categories(product_id)

    return render_template('products/view_product.html',
                           product=product,
                           categories=list(categories))


def view(category=None):
    if category:
        products = queries.product_find_by_category(category)
    else:
        products = current_app.db.Product.find()

    return products
