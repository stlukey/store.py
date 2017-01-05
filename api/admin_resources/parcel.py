from flask import request
from ..utils import Resource, easypost, check_data
from ..resources.products import pass_product


class ProductParcel(Resource):
    decorators = [pass_product]

    def post(self, product):
        REQUIRED = [
            'length', 'width',
            'height', 'weight'
        ]
        data = request.get_json(force=True)

        # Check parcel data.
        allowed, resp = check_data(data, REQUIRED, True)
        if not allowed:
            return resp

        parcel = easypost.Parcel.create(**data)

        print(parcel.id)
        product.update(dict(parcel_id=parcel.id))

        return product


def register_resources(admin_api):
    admin_api.add_resource(ProductParcel, '/parcel/<ObjectID:id>')
