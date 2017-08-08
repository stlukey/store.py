from flask import send_file, redirect
from flask_restful import Resource
from bson.objectid import ObjectId

from .models import Image as GridImage, SetImage
from ...utils import JSONResponse

ERROR_IMAGE_NOT_FOUND = "The image could not be found."


class Image(Resource):
    def get(self, id):
        if id == 'placeholder':
            return redirect('https://placehold.it/410x308')

        id = ObjectId(id)
        image = GridImage(id)

        if not image.exists:
            return JSONResponse(ERROR_IMAGE_NOT_FOUND, status=404)

        return send_file(image.data, mimetype='image/jpeg')

class SImage(Resource):
    def get(self, id):
        si = SetImage(id)

        if not si.exists:
            return JSONResponse(ERROR_IMAGE_NOT_FOUND, status=404)

        image = GridImage(ObjectId(si['image']))
        if not image.exists:
            return JSONResponse(ERROR_IMAGE_NOT_FOUND, status=404)

        return redirect(image.url)



def register_resources(api):
    api.add_resource(Image, '/images/<id>.jpg')
    api.add_resource(SImage, '/simages/<id>.jpg')
