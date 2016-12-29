from flask import request

from ..utils import check_data
from ..resources.pages import Pages, Page, models


class AdminPages(Pages):
    pass


class AdminPage(Page):
    def put(self, id):
        REQUIRED = ['content']
        data = request.get_json(force=True)
        # Check product data.
        allowed, resp = check_data(data, REQUIRED)
        if not allowed:
            return resp

        page = models.Page(id)
        page.update(_set=data)
        return page


def register_resources(admin_api):
    admin_api.add_resource(AdminPages, '/pages')
    admin_api.add_resource(AdminPage, '/pages/<id>')
