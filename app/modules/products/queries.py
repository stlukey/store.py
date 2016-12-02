from flask import current_app, abort
from bson.objectid import ObjectId

from bson import errors as bson_errors
from gridfs import errors as gridfs_errors


def product_get(product_id):
    if not isinstance(product_id, ObjectId):
        product_id = ObjectId(product_id)

    return current_app.db.Product.get_from_id(product_id)


def product_get_image(product, file_name):
    with product.fs.get_last_version('images/{}'.format(file_name)) as f:
            return f.read()


def product_find_by_category(category):
    category = current_app.db.Category.find_one({'name': category})
    products = current_app.db.ProductToCategory.find(
        {'category._id': category._id}
    )
    for product in products:
        yield product['product']


def product_find_categories(product):
    if hasattr(product, '_id'):
        product = product._id

    for category in list(current_app.db
                                    .ProductToCategory
                                    .find({'product._id': product})):
        yield category['category']['name']


def product_get_or_abort(product_id):
    try:
        product = product_get(product_id)
        if not product:
            abort(404)
    except bson_errors.InvalidId:
        abort(404)

    return product


def product_get_image_or_abort(product, file_name):
    try:
        return product_get_image(product, file_name)
    except gridfs_errors.NoFile:
        abort(404)
