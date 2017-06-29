from ..utils import Resource
from ..resources.users.models import requires_admin

class AdminResource(Resource):
	method_decorators = [requires_admin] + []
