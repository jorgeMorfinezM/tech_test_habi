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
import logging
from datetime import datetime
from pytz import timezone
from sqlalchemy_filters import apply_filters
from sqlalchemy import Column, Numeric, Integer, String, Date, Time, Sequence, Float
from db_controller.database_backend import *
from db_controller import mvc_exceptions as mvc_exc

cfg_db = get_config_settings_db()

STATUS_ID_SEQ = Sequence('status_id_seq')  # define sequence explicitly


class StatusModel(Base):
    r"""
    Class to instance the data of VehicleModel on the database.
    Transactions:
     - Insert: Add data to the database if not exists.
     - Update: Update data on the database if exists.
     - Delete:
     - Select:
    """

    __tablename__ = cfg_db.status_property_table

    id_status = Column('id', Integer, STATUS_ID_SEQ, primary_key=True, server_default=STATUS_ID_SEQ.next_value())
    name_status = Column('name', String, nullable=False)
    label_status = Column('label', String, nullable=False)

    def __init__(self, data_status):

        self.name_status = data_status.get('name_status')
        self.label_status = data_status.get('label_status')

    def check_if_row_exists(self, session, data):

        row_exists = None
        status_id = 0

        try:
            # for example to check if the insert on db is correct
            status_row = self.get_status_id(session, data)

            if status_row is not None:
                status_id = status_row.id_status
            else:
                status_id = 0

            logger.info('Status Row ID in DB: %s', str(status_id))

            row_exists = session.query(StatusModel).filter(StatusModel.id_status == status_id).scalar()

            logger.info('Row to data: {}, Exists: %s'.format(data), str(row_exists))

        except SQLAlchemyError as exc:
            row_exists = None
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('name_status'),
                                                                    str(str(exc.args) + ':' + str(exc.code)))
            )
        finally:
            session.close()

        return row_exists

    def insert_data(self, session, data):

        endpoint_response = None

        if not self.check_if_row_exists(session, data):

            try:

                new_row = StatusModel(data)

                logger.info('New Row JefeSicario: %s', str(new_row.nombre_jefe))

                session.add(new_row)

                status_row = self.get_status_id(session, data)

                logger.info('StatusModel data Id: %s', str(status_row))

                session.flush()

                data['id_status'] = status_row.id_status

                # check insert correct
                row_inserted = self.get_one_status(session, data)

                logger.info('Data Status inserted: %s, Original Data: {}'.format(data), str(row_inserted))

                if row_inserted:
                    endpoint_response = json.dumps({
                        "id_status": row_inserted.id_row,
                        "name_status": row_inserted.name_status,
                        "label_status": row_inserted.label_status
                    })

            except SQLAlchemyError as exc:
                endpoint_response = None
                session.rollback()
                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('name_status'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    def update_data(self, session, data):

        endpoint_response = None

        if self.check_if_row_exists(session, data):

            try:

                status_row = self.get_status_id(session, data)

                logger.info('StatusModel data Id: %s', str(status_row))

                # update row to database
                session.query(StatusModel).filter(StatusModel.id_status == status_row.id_status).\
                    update({"name_status": data.get('name_status'),
                            "label_status": data.get('label_status')},
                           synchronize_session='fetch')

                session.flush()

                data['id_status'] = status_row.id_status

                # check update correct
                row_updated = self.get_one_status(session, data)

                logger.info('Data Updated: %s', str(row_updated))

                if row_updated:
                    logger.info('Data Status updated')

                    endpoint_response = json.dumps({
                        "id_status": row_updated.id_row,
                        "name_status": row_updated.name_status,
                        "label_status": row_updated.label_status
                    })

            except SQLAlchemyError as exc:
                endpoint_response = None
                session.rollback()
                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('name_status'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    def delete_data(self, session, data):

        endpoint_response = None

        try:

            status_row = self.get_status_id(session, data)

            logger.info('StatusModel data Id: %s', str(status_row))

            session.query(StatusModel).filter(StatusModel.id_jefe == status_row.id_status).delete()

            session.flush()

            data['id_status'] = status_row.id_status

            # check delete correct
            row_deleted = self.get_one_status(session, data)

            if not row_deleted or row_deleted is None:
                logger.info('Status deleted')

                endpoint_response = json.dumps({
                    "id_status": status_row.id_row,
                    "name_status": status_row.name_status,
                    "label_status": status_row.label_status
                })

        except SQLAlchemyError as exc:
            endpoint_response = None
            session.rollback()
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('name_status'),
                                                                    str(str(exc.args) + ':' + str(exc.code)))
            )
        finally:
            session.close()

        return endpoint_response

    @staticmethod
    def get_status_id(session, data):

        row_status = None

        try:

            row_exists = session.query(StatusModel).\
                filter(StatusModel.name_status == data.get('name_status')).scalar()

            logger.info('Row Data Status Exists on DB: %s', str(row_exists))

            if row_exists:

                row_status = session.query(StatusModel). \
                    filter(StatusModel.name_status == data.get('name_status')).one()

                logger.info('Row ID Status data from database object: {}'.format(str(row_status)))

        except SQLAlchemyError as exc:

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('name_status'), StatusModel.__tablename__, str(str(exc.args) + ':' +
                                                                            str(exc.code))
                )
            )

        finally:
            session.close()

        return row_status

    def get_one_status(self, session, data):
        row = None

        try:
            row_status = self.get_status_id(session, data)

            row = session.query(StatusModel).filter(StatusModel.id_status == row_status.id_status).\
                filter(StatusModel.name_status == data.get('name_status')).one()

            if row:
                logger.info('Data Inversion on Db: %s',
                            'Cuenta: {}, Monto inversion: {}, Inversion Estatus: {}'.format(row.cuenta,
                                                                                            row.monto,
                                                                                            row.estatus))

        except SQLAlchemyError as exc:
            row = None
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))

            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('name_status'), StatusModel.__tablename__, str(str(exc.args) + ':' + str(exc.code))
                )
            )

        finally:
            session.close()

        return row

    @staticmethod
    def get_all_status(session):

        all_status = None
        status_data = []

        all_status = session.query(StatusModel).all()

        for status in all_status:

            status_id = status.id_status
            name_status = status.name_status
            label_status = status.label_status

            status_data += [{
                "Status": {
                    "id_status": status_id,
                    "Name": name_status,
                    "Label": label_status
                }
            }]

        return json.dumps(status_data)

    def __repr__(self):
        return "<StatusModel(id_status='%s', name_status='%s', label_status='%s')>" % \
               (self.id_status, self.name_status, self.label_status)
