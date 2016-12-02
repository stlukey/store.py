#!/usr/bin/env python3
"""
"""

from flask import Blueprint, render_template, current_app, make_response

from . import queries

products = Blueprint('products', __name__)


@products.route('/<product_id>/images/<file_name>')
def images(product_id, file_name):
    product = queries.product_get_or_abort(product_id)
    image = queries.product_get_image_or_abort(product, file_name)
    response = make_response(image)
    response.mimetype = 'image/jpeg'
    return response


@products.route('/<product_id>')
@products.route('/<product_id>/<product_name>')
def view_product(product_id, product_name=None):
    product = queries.product_get_or_abort(product_id)
    categories = queries.product_find_categories(product)

    return render_template('products/view_product.html',
                           product=product,
                           categories=list(categories))


def view(category=None):
    if category:
        products = queries.product_find_by_category(category)
    else:
        products = current_app.db.Product.find()

    return products
