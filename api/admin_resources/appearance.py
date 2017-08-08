from flask import request

from ..utils import check_data, Resource, JSONResponse
from ..resources.images.models import SetImage

IMAGES_SET_MESSAGE =\
"""Image settings saved."""

class SetImagesAdmin(Resource):
    def get(self):
        return {i['_id']: i['image'] for i in SetImage.find()}

    def put(self):
        REQUIRED = [i['_id'] for i in SetImage.find()]
        data = request.get_json(force=True)
        # Check product data.
        allowed, resp = check_data(data, REQUIRED)
        if not allowed:
            return resp

        for _id, image in data.items():
            si = SetImage(_id)
            si['image'] = image
            si.update()

        return JSONResponse(IMAGES_SET_MESSAGE, list(SetImage.find()))


def register_resources(admin_api):
    admin_api.add_resource(SetImagesAdmin, '/appearance/images')
