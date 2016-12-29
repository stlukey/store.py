from ..utils import Resource
from ..resources.users import models


class UsersAdmin(Resource):
    def get(self):
        return models.User.find(active=True)


def register_resources(admin_api):
    admin_api.add_resource(UsersAdmin, '/users')
