from ...utils import Resource
from . import models


class Page(Resource):
    def get(self, id):
        page = models.Page(id)
        if not page.exists:
            return "NOT FOUND", 404
        return page


class Pages(Resource):
    def get(self):
        return models.Page.find()


def register_resources(api):
    api.add_resource(Pages, '/pages')
    api.add_resource(Page, '/pages/<id>')
