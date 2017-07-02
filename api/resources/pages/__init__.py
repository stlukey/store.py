from ...utils import Resource
from . import models

ERROR_PAGE_NOT_FOUND =\
"That page can not be found."


class Page(Resource):
    def get(self, id):
        page = models.Page(id)
        if not page.exists:
            return ERROR_PAGE_NOT_FOUND, 404
        return page


class Pages(Resource):
    def get(self):
        return models.Page.find()


def register_resources(api):
    api.add_resource(Pages, '/pages')
    api.add_resource(Page, '/pages/<id>')
