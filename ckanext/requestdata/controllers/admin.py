try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config
from ckan.plugins import toolkit
from ckan.controllers.admin import AdminController
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic

get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized

c = base.c
redirect = base.redirect
request = base.request

CACHE_PARAMETERS = ['__cache', '__no_cache__']

class AdminController(AdminController):
    ctrl = 'ckanext.requestdata.controllers.admin:AdminController'

    def email(self):
        '''Email template admin tab.

        :param :
        :type

        '''
        data = request.POST
        print data
        if 'save' in data:
            try:
                data_dict = dict(request.POST)
                print data_dict
                del data_dict['save']

                data = logic.get_action('config_option_update')(
                    {'user': c.user}, data_dict)


            except logic.ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                vars = {'data': data, 'errors': errors,
                        'error_summary': error_summary}
                return base.render('admin/email.html', extra_vars=vars)

            h.redirect_to(controller=self.ctrl, action='email')

        schema = logic.schema.update_configuration_schema()
        data = {}
        for key in schema:
            data[key] = config.get(key)

        vars = {'data': data, 'errors': {}}
        return toolkit.render('admin/email.html',extra_vars=vars)

    def requests_data(self):
        '''
        Return all of the data requests in admin panel

        :return:
        '''

        return toolkit.render('admin/all_requests_data.html')