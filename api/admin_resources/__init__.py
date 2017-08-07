from flask_restful import Api

from flask import make_response
from bson.json_util import dumps

from ..resources.users.models import requires_admin
from ..utils import output_json
from ..config import TESTING

from . import products
from . import users
from . import orders
from . import shipments
from . import pages
from . import images



def register_resources(admin):
    if not TESTING:
        admin.before_request(requires_admin)

    admin_api = Api(admin)
    admin_api.representations = {
        'application/json': output_json
    }

    products.register_resources(admin_api)
    users.register_resources(admin_api)
    orders.register_resources(admin_api)
    shipments.register_resources(admin_api)
    pages.register_resources(admin_api)
    images.register_resources(admin_api)
