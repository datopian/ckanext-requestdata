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


class PackageController(BaseController):

    def make_active(self, pkg_name):
        '''Makes a package active.

        :param pkg_name: The name of a package.
        :type pkg_name: string

        '''

        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}

        data_dict = {
            'id': pkg_name,
            'state': 'active'
        }

        try:
            get_action('package_patch')(context, data_dict)
        except NotAuthorized:
            abort(403, _('Unauthorized to update this dataset.'))
        except NotFound:
            abort(404, _('The dataset {id} could not be found.').format(id=id))

        url = h.url_for(controller='package', action='read', id=id)
        redirect(url)
