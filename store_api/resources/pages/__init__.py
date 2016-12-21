from ...utils import Resource
from . import models


class Page(Resource):
    def get(self, id):
        page = models.Page(id)
        if not page.exists:
            return "NOT FOUND", 404
        return page


def register_resources(api):
    api.add_resource(Page, '/pages/<string:id>')
