from ckan.lib import base
from ckan import logic
from ckan.plugins import toolkit

get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized

redirect = base.redirect
abort = base.abort
BaseController = base.BaseController


class AdminController(BaseController):

    def email(self):
        '''Email template admin tab.

        :param :
        :type

        '''
        return toolkit.render('admin/email.html')