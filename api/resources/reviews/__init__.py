from ...utils import Resource, check_data
from . import models
from ..products.models import Product
from ..users import requires_token
from flask import request

ERROR_REVIEW_EXISTS = "You have already left a review for that item."
ERROR_REVIEW_NOT_FOUND = "That review can not be found, please try again."
REVIEW_CREATED_MESSAGE = "Thank you for reviewing our product."

ERROR_PRODUCT_NOT_FOUND =  "That product can not be found."
def pass_product(func):
    def wrapped(id, *args, **kwargs):
        product = Product(id)
        if not product.exists:
            return ERROR_PRODUCT_NOT_FOUND, 404

        return func(product, *args, **kwargs)
    return wrapped

class Review(Resource):
    decorators = [requires_token, pass_product]
    def post(self, user, product):
        REQUIRED = [
            'rating', 'description'
        ]
        data = request.get_json(force=True)
        allowed, resp = check_data(data, REQUIRED, REQUIRED)
        if not allowed:
            return resp

        if models.Review(user=user.id, product=product.id).exists:
            return ERROR_REVIEW_EXISTS, 400

        data['user'] = user.id
        data['product'] = product.id

        models.Review.new(**data)
        return REVIEW_CREATED_MESSAGE, 200

    def get(self, user, product):
        review = models.Review(user=user.id, product=product.id)
        if not review.exists:
            return ERROR_REVIEW_NOT_FOUND, 404

        return review





def register_resources(api):
    api.add_resource(Review, '/review/<ObjectID:id>')
