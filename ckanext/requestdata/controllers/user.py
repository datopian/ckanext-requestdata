from ckan.lib import base
from ckan.common import c, _
from ckan import logic
import ckan.model as model
import ckan.lib.helpers as h

get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized

redirect = base.redirect
abort = base.abort
BaseController = base.BaseController


class UserController(BaseController):

    def my_requests(self):
        return
