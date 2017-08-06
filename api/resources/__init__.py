from flask_restful import Api

from flask import make_response
from bson.json_util import dumps

from ..utils import output_json


from . import products
from . import users
from . import cart
from . import pages
from . import orders
from . import reviews
from . import images



def register_resources(app):
    api = Api(app)
    api.representations = {
        'application/json': output_json
    }

    products.register_resources(api)
    users.register_resources(api)
    cart.register_resources(api)
    pages.register_resources(api)
    orders.register_resources(api)
    reviews.register_resources(api)
    images.register_resources(api)
