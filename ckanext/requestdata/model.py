import logging
import datetime

from sqlalchemy import Table, Column ,Index, ForeignKey
from sqlalchemy import types, func

from sqlalchemy.engine.reflection import Inspector
from ckan.model.meta import metadata, mapper, Session, engine
from ckan.model.types import make_uuid
from ckan.model.domain_object import DomainObject

log = logging.getLogger(__name__)

request_data_table = None
user_notification_table = None
maintainers_table = None
request_data_counters_table = None

def setup():
    if request_data_table is None:
        define_request_data_table()
        log.debug('Requestdata table defined in memory.')

        if not request_data_table.exists():
            request_data_table.create()
    else:
        log.debug('Requestdata table already exists.')
        inspector = Inspector.from_engine(engine)

        index_names =\
            [index['name'] for index in
                inspector.get_indexes('ckanext_requestdata_requests')]

        if 'ckanext_requestdata_requests_id_idx' not in index_names:
            log.debug('Creating index for ckanext_requestdata.')
            Index('ckanext_requestdata_requests_id_idx',
                  request_data_table.c.id).create()

    if user_notification_table is None:
        define_user_notification_table()
        log.debug('UserNotification table defined in memory.')

        if not user_notification_table.exists():
            user_notification_table.create()
    else:
        log.debug('UserNotification table already exists.')
        inspector = Inspector.from_engine(engine)

        index_names = \
            [index['name'] for index in
             inspector.get_indexes('ckanext_requestdata_user_notification')]

        if 'ckanext_requestdata_user_notification_id_idx' not in index_names:
            log.debug('Creating index for ckanext_user_notification.')
            Index('ckanext_requestdata_user_notification_id_idx',
                  user_notification_table.c.id).create()

    if maintainers_table is None:
        define_maintainers_table()
        log.debug('Maintainers table defined in memory.')

        if not maintainers_table.exists():
            maintainers_table.create()
    else:
        log.debug('Maintainers table already exists.')
        inspector = Inspector.from_engine(engine)

        index_names = \
            [index['name'] for index in
             inspector.get_indexes('ckanext_requestdata_maintainers')]

        if 'ckanext_requestdata_maintainers_id_idx' not in index_names:
            log.debug('Creating index for ckanext_user_notification.')
            Index('ckanext_requestdata_maintainers_id_idx',
                  maintainers_table.c.id).create()

    if request_data_counters_table is None:
        define_request_data_counters_table()
        log.debug('Request data counters table defined in memory.')

        if not request_data_counters_table.exists():
            request_data_counters_table.create()
    else:
        log.debug('Request data counters table already exists.')
        inspector = Inspector.from_engine(engine)

        index_names = \
            [index['name'] for index in
             inspector.get_indexes('ckanext_requestdata_counters')]

        if 'ckanext_requestdata_counters_id_idx' not in index_names:
            log.debug('Creating index for ckanext_request_data_counters.')
            Index('ckanext_requestdata_counters_id_idx',
                  request_data_counters_table.c.id).create()


class ckanextRequestdata(DomainObject):
    @classmethod
    def get(self, **kwds):
        '''Finds a single entity in the table.

        '''

        query = Session.query(self).autoflush(False)
        query = query.filter_by(**kwds).first()

        return query

    @classmethod
    def search(self, order='modified_at desc', **kwds):
        '''Finds entities in the table that satisfy certain criteria.

        :param order: Order rows by specified column.
        :type order: string

        '''

        query = Session.query(self).autoflush(False)
        query = query.filter_by(**kwds)
        query = query.order_by(order)

        return query.all()

    @classmethod
    def search_by_maintainers(self,id,order='modified_at desc'):
        '''Finds all of the requests for the specific maintainer

        :param id: User is
        :type id: string

        '''
        maintainer_id = id;
        requests= Session.query(ckanextRequestdata,ckanextMaintainers).join(ckanextMaintainers)\
                         .filter(ckanextRequestdata.id == ckanextMaintainers.request_data_id, ckanextMaintainers.maintainer_id == maintainer_id)\
                         .order_by(order).all()

        requests_data = []
        for r in requests:
            request = {}
            request.update({
                'id': r.ckanextRequestdata.id,
                'sender_name':r.ckanextRequestdata.sender_name,
                'sender_user_id':r.ckanextRequestdata.sender_user_id,
                'organization':r.ckanextRequestdata.organization,
                'email_address':r.ckanextRequestdata.email_address,
                'message_content': r.ckanextRequestdata.message_content,
                'package_id':r.ckanextRequestdata.package_id,
                'state':r.ckanextRequestdata.state,
                'data_shared':r.ckanextRequestdata.data_shared,
                'rejected':r.ckanextRequestdata.rejected,
                'created_at':r.ckanextRequestdata.created_at,
                'modified_at':r.ckanextRequestdata.modified_at,
                'maintainer_id': r.ckanextMaintainers.maintainer_id,
                'email': r.ckanextMaintainers.email
            })
            requests_data.append(request)
        return requests_data


def define_request_data_table():
    global request_data_table

    request_data_table = Table('ckanext_requestdata_requests', metadata,
                               Column('id', types.UnicodeText,
                                      primary_key=True,
                                      default=make_uuid),
                               Column('sender_name', types.UnicodeText,
                                      nullable=False),
                               Column('sender_user_id', types.UnicodeText,
                                      nullable=False),
                               Column('organization', types.UnicodeText,
                                      nullable=False),
                               Column('email_address', types.UnicodeText,
                                      nullable=False),
                               Column('message_content', types.UnicodeText,
                                      nullable=False),
                               Column('package_id', types.UnicodeText,
                                      nullable=False),
                               Column('state', types.UnicodeText,
                                      default='new'),
                               Column('data_shared', types.Boolean,
                                      default=False),
                               Column('rejected', types.Boolean,
                                      default=False),
                               Column('created_at', types.DateTime,
                                      default=datetime.datetime.now),
                               Column('modified_at', types.DateTime,
                                      default=datetime.datetime.now),
                               Index('ckanext_requestdata_requests_id_idx', 'id'))

    mapper(
        ckanextRequestdata,
        request_data_table
    )


class ckanextUserNotification(DomainObject):
    @classmethod
    def get(self, **kwds):
        '''Finds a single entity in the table.

        '''

        query = Session.query(self).autoflush(False)
        query = query.filter_by(**kwds).first()
        return query

    @classmethod
    def search(self,**kwds):
        '''Finds entities in the table that satisfy certain criteria.

        :param order: Order rows by specified column.
        :type order: string

        '''

        query = Session.query(self).autoflush(False)
        query = query.filter_by(**kwds)

        return query.all()


def define_user_notification_table():
    global user_notification_table

    user_notification_table = Table('ckanext_requestdata_user_notification', metadata,
                               Column('id', types.UnicodeText,
                                      primary_key=True,
                                      default=make_uuid),
                               Column('package_maintainer_id', types.UnicodeText,
                                      nullable=False),
                               Column('seen', types.Boolean,
                                      default=False),
                               Index('ckanext_requestdata_user_notification_id_idx', 'id'))

    mapper(
        ckanextUserNotification,
        user_notification_table
    )

class ckanextMaintainers(DomainObject):
    @classmethod
    def get(self, **kwds):
        '''Finds a single entity in the table.

        '''

        query = Session.query(self).autoflush(False)
        query = query.filter_by(**kwds).first()

        return query

    @classmethod
    def search(self,**kwds):
        '''Finds entities in the table that satisfy certain criteria.

        :param order: Order rows by specified column.
        :type order: string

        '''

        query = Session.query(self).autoflush(False)
        query = query.filter_by(**kwds)

        return query.all()

    @classmethod
    def insert_all(self, maintainers, requestdata_id):
        '''Finds entities in the table that satisfy certain criteria.

        :param order: Order rows by specified column.
        :type order: string

        '''
        Session.add_all(maintainers)
        Session.commit()
        data_dict = {
            'requestdata_id': requestdata_id
        }
        return data_dict


def define_maintainers_table():
    global maintainers_table

    maintainers_table = Table('ckanext_requestdata_maintainers', metadata,
                                Column('id', types.UnicodeText, primary_key=True, default=make_uuid),

                                Column('request_data_id', types.UnicodeText, ForeignKey('ckanext_requestdata_requests.id')),
                                Column('maintainer_id', types.UnicodeText),
                                Column('email', types.UnicodeText),
                                Index('ckanext_requestdata_maintainers_id_idx', 'id')
                                )

    mapper(
        ckanextMaintainers,
        maintainers_table
    )


class ckanextRequestDataCounters(DomainObject):
    @classmethod
    def get(self, **kwds):
        '''Finds a single entity in the table.

        '''

        query = Session.query(self).autoflush(False)
        query = query.filter_by(**kwds).first()

        return query

    @classmethod
    def search(self, **kwds):
        '''Finds entities in the table that satisfy certain criteria.

        :param order: Order rows by specified column.
        :type order: string

        '''

        request = Session.query(func.sum(ckanextRequestDataCounters.requests)).all()
        replied = Session.query(func.sum(ckanextRequestDataCounters.replied)).all()
        declined = Session.query(func.sum(ckanextRequestDataCounters.declined)).all()
        shared = Session.query(func.sum(ckanextRequestDataCounters.shared)).all()
        counters = {
            'requests' : request,
            'replied': replied,
            'declined': declined,
            'shared' : shared
        }

        return counters

    @classmethod
    def search_by_organization(self, **kwds):
        '''Finds entities in the table that satisfy certain criteria.

        :param order: Order rows by specified column.
        :type order: string

        '''

        request = Session.query(func.sum(ckanextRequestDataCounters.requests))
        request = request.filter_by(**kwds).all()
        replied = Session.query(func.sum(ckanextRequestDataCounters.replied))
        replied = replied.filter_by(**kwds).all()
        declined = Session.query(func.sum(ckanextRequestDataCounters.declined))
        declined = declined.filter_by(**kwds).all()
        shared = Session.query(func.sum(ckanextRequestDataCounters.shared))
        shared = shared.filter_by(**kwds).all()
        counters = {
            'requests' : request,
            'replied': replied,
            'declined': declined,
            'shared' : shared
        }

        return counters


def define_request_data_counters_table():
    global request_data_counters_table

    request_data_counters_table = Table('ckanext_requestdata_counters', metadata,
                                Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
                                Column('package_id', types.UnicodeText),
                                Column('org_id', types.UnicodeText),
                                Column('requests', types.Integer,default=0),
                                Column('replied', types.Integer,default=0),
                                Column('declined', types.Integer,default=0),
                                Column('shared', types.Integer,default=0),
                                Index('ckanext_requestdata_counters_id_idx', 'id')
                                )

    mapper(
        ckanextRequestDataCounters,
        request_data_counters_table
    )
