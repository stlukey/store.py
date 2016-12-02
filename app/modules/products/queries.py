from flask import current_app


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
