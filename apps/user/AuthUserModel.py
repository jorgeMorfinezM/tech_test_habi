# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later


PostgreSQL DB backend.

Each one of the CRUD operations should be able to open a database connection if
there isn't already one available (check if there are any issues with this).

Documentation:
    About the Bank Bot data on the database to generate CRUD operations from endpoint of the API:
    - Insert data
    - Update data
    - Delete data
    - Search data

"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021"
__license__ = ""
__history__ = """ """
__version__ = "1.21.F21.1 ($Rev: 1 $)"

import json
from sqlalchemy import Column, Boolean, Integer, String, Date, Sequence
from db_controller.database_backend import *
from db_controller import mvc_exceptions as mvc_exc

cfg_db = get_config_settings_db()

USER_ID_SEQ = Sequence('user_id_seq')  # define sequence explicitly


class AuthUserModel(Base):
    r"""
    Class to instance the data of VehicleModel on the database.
    Transactions:
     - Insert: Add data to the database if not exists.
     - Update: Update data on the database if exists.
     - Delete:
     - Select:
    """

    __tablename__ = cfg_db.hit_table

    user_id = Column('id', Integer, USER_ID_SEQ, primary_key=True, server_default=USER_ID_SEQ.next_value())
    username = Column('username', String, nullable=False)
    password = Column('password', Date, nullable=False)
    first_name = Column('first_name', String, nullable=False)
    last_name = Column('last_name', String, nullable=False)
    email = Column('email', String, nullable=False)
    date_joined = Column('date_joined', Date, nullable=False)
    last_login = Column('last_login', Date, nullable=True)
    is_active = Column('is_active', Boolean, nullable=False)
    is_staff = Column('is_staff', Boolean, nullable=True)
    is_superuser = Column('is_superuser', Boolean, nullable=True)

    def __init__(self, data_user):

        self.user_name = data_user.get('username')
        self.password = data_user.get('password')
        self.email = data_user.get('email')
        self.first_name = data_user.get('first_name')
        self.last_name = data_user.get('last_name')
        self.is_active = data_user.get('is_active')
        self.is_staff = data_user.get('is_staff')
        self.is_superuser = data_user.get('is_superuser')

    def check_if_row_exists(self, session, data):

        row_exists = None
        user_id = 0

        try:

            user_row = self.get_user_by_id(session, data)

            if user_row is not None:
                user_id = user_row.user_id
            else:
                user_id = 0

            logger.info('User Row object in DB: %s', str(user_row))

            row_exists = session.query(AuthUserModel).filter(AuthUserModel.user_id == user_id).\
                filter(AuthUserModel.username == data.get('username')).scalar()

            logger.info('Row to data: {}, Exists: %s'.format(data), str(row_exists))

        except SQLAlchemyError as exc:
            row_exists = None

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('username'),
                                                                    str(str(exc.args) + ':' + str(exc.code)))
            )
        finally:
            session.close()

        return row_exists

    def insert_data(self, session, data):

        endpoint_response = None

        if not self.check_if_row_exists(session, data):

            try:

                self.date_joined = get_current_date(session)  # date_joined

                data['date_joined'] = self.date_joined

                new_row = AuthUserModel(data)

                logger.info('New Row User name: %s', str(new_row.username))

                session.add(new_row)

                user_row = self.get_user_by_id(session, data)

                logger.info('User ID Inserted: %s', str(user_row.user_id))

                session.flush()

                data['user_id'] = user_row.user_id

                # check insert correct
                row_inserted = self.get_one_user(session, data)

                logger.info('Data Bank inserted: %s, Original Data: {}'.format(data), str(row_inserted))

                if row_inserted:

                    logger.info('Bank inserted is: %s', 'Username: {}, '
                                                        'Email: {} '
                                                        'FirstName: {}'.format(row_inserted.username,
                                                                               row_inserted.email,
                                                                               row_inserted.first_name))

                    endpoint_response = json.dumps({
                        "Username": data.get('username'),
                        "Password": data.get('password'),
                        "Email": data.get('email'),
                        "FirstName": data.get('first_name'),
                        "LastName": data.get('last_name'),
                        "IsActive": data.get('is_active'),
                        "IsStaff": data.get('is_staff'),
                        "IsSuperUser": data.get('is_superuser'),
                        "DateJoined": data.get('date_joined')
                    })

            except SQLAlchemyError as exc:
                endpoint_response = None
                session.rollback()
                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    def update_data(self, session, data):

        endpoint_response = None

        if self.check_if_row_exists(session, data):

            try:

                # update row to database
                session.query(AuthUserModel).filter(AuthUserModel.user_id == data.get('user_id')).\
                    update({"username": data.get('username'),
                            "password": data.get('password'),
                            "email": data.get('email'),
                            "first_name": data.get('first_name'),
                            "last_name": data.get('last_name'),
                            "is_active": data.get('is_active'),
                            "is_staff": data.get('is_staff'),
                            "is_superuser": data.get('is_superuser'),
                            "date_joined": get_current_date(session)},
                           synchronize_session='fetch')

                session.flush()

                # check update correct
                row_updated = self.get_one_user(session, data)

                logger.info('Data Updated: %s', str(row_updated))

                if row_updated:
                    logger.info('Data User updated')

                    endpoint_response = json.dumps({
                        "Username": row_updated.username,
                        "Password": row_updated.password,
                        "Email": row_updated.email,
                        "FirstName": row_updated.first_name,
                        "LastName": row_updated.last_name,
                        "IsActive": row_updated.is_active,
                        "IsStaff": row_updated.is_staff,
                        "IsSuperUser": row_updated.is_superuser,
                        "DateJoined": row_updated.date_joined
                    })

            except SQLAlchemyError as exc:
                session.rollback()
                endpoint_response = None

                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('username'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    # Transaction to update user' password  hashed on db to authenticate - PATCH
    def user_update_password(self, session, data):
        r"""
        Transaction to update password hashed of a user to authenticate on the API correctly.

        :param session: The user name to update password hashed.
        :param data: The password hashed to authenticate on the API.
        """

        endpoint_response = None

        if self.check_if_row_exists(session, data):

            try:

                # update row to database
                session.query(AuthUserModel).filter(AuthUserModel.user_id == data.get('user_id')). \
                    update({"password": data.get('password')},
                           synchronize_session='fetch')

                session.flush()

                # check update correct
                row_updated = self.get_one_user(session, data)

                logger.info('Data Updated: %s', str(row_updated))

                if row_updated:
                    logger.info('Data User updated')

                    endpoint_response = json.dumps({
                        "Username": row_updated.username,
                        "Password": row_updated.password,
                        "Email": row_updated.email,
                        "FirstName": row_updated.first_name,
                        "LastName": row_updated.last_name,
                        "IsActive": row_updated.is_active,
                        "IsStaff": row_updated.is_staff,
                        "IsSuperUser": row_updated.is_superuser,
                        "DateJoined": row_updated.date_joined
                    })

            except SQLAlchemyError as exc:
                session.rollback()
                endpoint_response = None

                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('username'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    def delete_data(self, session, data):

        endpoint_response = None

        try:

            user_row = self.get_user_by_id(session, data)

            session.query(AuthUserModel).filter(AuthUserModel.user_id == user_row.user_id).delete()

            session.flush()

            data['user_id'] = user_row.user_id

            session.flush()

            # check update correct
            row_deleted = self.get_one_user(session, data)

            if row_deleted is None:
                logger.info('User deleted')

                endpoint_response = json.dumps({
                    "Username": data.get('username'),
                    "Password": data.get('password'),
                    "Email": data.get('email'),
                    "FirstName": data.get('first_name'),
                    "LastName": data.get('last_name'),
                    "IsActive": data.get('is_active'),
                    "IsStaff": data.get('is_staff'),
                    "IsSuperUser": data.get('is_superuser'),
                    "DateJoined": data.get('date_joined')
                })

        except SQLAlchemyError as exc:
            session.rollback()
            endpoint_response = None
            logger.exception('An exception was occurred while execute transactions: %s',
                             str(str(exc.args) + ':' + str(exc.code)))

            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('username'),
                                                                    str(str(exc.args) + ':' + str(exc.code)))
            )

        finally:
            session.close()

        return endpoint_response

    def get_one_user(self, session, data):

        row_user = None

        try:

            user_row = self.get_user_by_id(session, data)

            if session.query(AuthUserModel).filter(AuthUserModel.user_id == user_row.user_id).scalar():

                row_user = session.query(AuthUserModel).filter(AuthUserModel.user_id == user_row.user_id).one()

                if row_user:
                    logger.info('Data Bank on Db: %s',
                                'Bank Name: {}, Bank usaToken: {}, Bank Status: {}'.format(row_user.nombre_banco,
                                                                                           row_user.usa_token,
                                                                                           row_user.estatus_banco))

        except SQLAlchemyError as exc:
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('user_id'), AuthUserModel.__tablename__, str(str(exc.args) + ':' + str(exc.code))
                )
            )
        finally:
            session.close()

        return row_user

    @staticmethod
    def get_user_by_id(session, data):

        row = None

        try:

            row_exists = session.query(AuthUserModel).filter(AuthUserModel.username == data.get('username')). \
                filter(AuthUserModel.email == data.get('email')). \
                filter(AuthUserModel.first_name == data.get('first_name')).scalar()

            if row_exists:

                row = session.query(AuthUserModel).\
                    filter(AuthUserModel.username == data.get('username')).\
                    filter(AuthUserModel.email == data.get('email')).\
                    filter(AuthUserModel.first_name == data.get('first_name')).one()

                logger.info('Data User on Db: %s',
                            'Username: {}, Email: {}, First name: {}'.format(row.username,
                                                                             row.email,
                                                                             row.first_name))

        except SQLAlchemyError as exc:
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))

            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('email'), AuthUserModel.__tablename__, str(str(exc.args) + ':' + str(exc.code))
                )
            )

        finally:
            session.close()

        return row

    @staticmethod
    def get_all_users(session):

        all_users = None
        user_data = []
        data = dict()

        all_users = session.query(AuthUserModel).all()

        for user_rs in all_users:
            id_user = user_rs.id_user
            username = user_rs.username
            password = user_rs.password
            email = user_rs.email
            first_name = user_rs.first_name
            last_name = user_rs.last_name
            is_active = user_rs.is_active
            is_staff = user_rs.is_staff
            is_superuser = user_rs.is_superuser
            date_joined = user_rs.date_joined

            user_data += [{
                "AuthUser": {
                    "Id": id_user,
                    "Username": username,
                    "Password": password,
                    "Email": email,
                    "FirstName": first_name,
                    "LastName": last_name,
                    "IsActive": is_active,
                    "IsStaff": is_staff,
                    "IsSuperuser": is_superuser,
                    "DateJoined": date_joined
                }
            }]

        return json.dumps(user_data)

    def __repr__(self):
        return "<AuthUserModel(id_user='%s', username='%s', password='%s', email='%s', " \
               "first_name='%s', last_name='%s', is_active='%s', is_staff='%s', is_superuser='%s', " \
               "date_joined='%s')>" % (self.user_id, self.username, self.password, self.email, self.first_name,
                                       self.last_name, self.is_active, self.is_staff, self.is_superuser,
                                       self.date_joined)
