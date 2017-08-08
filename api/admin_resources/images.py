from flask import request

from ..utils import check_data, Resource, JSONResponse
from ..resources.images.models import Image

IMAGE_UPLOADED_MESSAGE = "Image uploaded sucessfully."
IMAGE_DELETED_MESSAGE = "Image deleted sucessfully."

ERROR_IMAGE_NOT_FOUND = "The image could not be found."
ERROR_INVALID_IMAGE = "The image is in a invalid format. " + \
                      "Only .jpg images are accepted. Please try again."
ERROR_MULTIPLE_IMAGES = "Please only upload one image at a time."


def valid_file(image):
    return image.content_type == 'image/jpeg'

class ImageAdmin(Resource):
    def delete(self, image_id):
        image = Image(image_id)
        if not image.exists:
            return ERROR_IMAGE_NOT_FOUND, 404

        image.delete()

        return IMAGE_DELETED_MESSAGE, 200

class ImagesAdmin(Resource):
    def get(self):
        return list(Image.find_all())

    def post(self):
        if len(request.files) != 1:
            return ERROR_MULTIPLE_IMAGES, 400

        f = request.files['file']
        if not valid_file(f):
            return ERROR_INVALID_IMAGE, 400

        image = Image.new(f)

        return JSONResponse(IMAGE_UPLOADED_MESSAGE, image._id)


def register_resources(admin_api):
    admin_api.add_resource(ImagesAdmin, '/images')
    admin_api.add_resource(ImageAdmin, '/images/<ObjectID:image_id>')
