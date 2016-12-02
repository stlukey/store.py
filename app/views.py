
from flask import Blueprint, current_app, render_template

store = Blueprint('store', __name__)


@store.route('/')
def store_front():
    popular = []
    while len(popular) < 4:
        product = current_app.db.Product.find_random()
        if product not in popular:
            popular.append(product)

    latest = [
        current_app.db.Product
                      .find_random(),
        current_app.db.Product
                      .find_random(),
        current_app.db.Product
                      .find_random()
    ]
    print(latest)

    return render_template('index.html',
                           most_popular=popular,
                           latest=latest)
