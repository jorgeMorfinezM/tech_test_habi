# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later


MySQL DB backend.

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
from apps.property.PropertyModel import PropertyModel
from apps.status.StatusModel import StatusModel
from sqlalchemy import Column, Integer, Date, Sequence
from db_controller.database_backend import *
from db_controller import mvc_exceptions as mvc_exc

cfg_db = get_config_settings_db()

STATUS_HISTORY_ID_SEQ = Sequence('status_history_id_seq')  # define sequence explicitly


class StatusHistoryModel(Base):
    r"""
    Class to instance the data of VehicleModel on the database.
    Transactions:
     - Insert: Add data to the database if not exists.
     - Update: Update data on the database if exists.
     - Delete:
     - Select:
    """

    __tablename__ = cfg_db.status_history_table

    id_history = Column('id', Integer, STATUS_HISTORY_ID_SEQ, primary_key=True,
                        server_default=STATUS_HISTORY_ID_SEQ.next_value())

    property_id = Column(
        'property_id',
        Integer,
        ForeignKey('property.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        unique=True
        # no need to add index=True, all FKs have indexes
    )

    property = relationship(PropertyModel,
                            backref=cfg_db.property_table.__str__())

    status_id = Column(
        'status_id',
        Integer,
        ForeignKey('status.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        unique=True
        # no need to add index=True, all FKs have indexes
    )

    status = relationship(StatusModel,
                          backref=cfg_db.status_property_table.__str__())

    update_date = Column('update_date', Date, nullable=False)

    def __init__(self, data_status):

        self.property_id = data_status.get('property_id')
        self.status_id = data_status.get('status_id')
        # para obtener la fecha de actualizacion que sera la de insercion de un nuevo registro
        # self.update_date = get_current_date(session)

    def check_if_row_exists(self, session, data):

        row_exists = None
        history_id = 0

        try:
            # for example to check if the insert on db is correct
            history_row = self.get_history_status_id(session, data)

            if history_row is not None:
                history_id = history_row.id_history
            else:
                history_id = 0

            logger.info('History Row object in DB: %s', str(history_row))

            row_exists = session.query(StatusHistoryModel).\
                filter(StatusHistoryModel.id_history == history_id).scalar()

            logger.info('Row to data: {}, Exists: %s'.format(data), str(row_exists))

        except SQLAlchemyError as exc:
            row_exists = None

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('property_id'),
                                                                    str(str(exc.args) + ':' + str(exc.code)))
            )
        finally:
            session.close()

        return row_exists

    def insert_data(self, session, data):

        endpoint_response = None

        if not self.check_if_row_exists(session, data):

            try:
                # para obtener la fecha de actualizacion que sera la de insercion de un nuevo registro
                self.update_date = get_current_date(session)

                data['update_date'] = self.update_date

                new_row = StatusHistoryModel(data)

                logger.info('New Row StatusHistory: %s', str(new_row.property_id))

                session.add(new_row)

                jefe_id = self.get_status_id(session, data).id_jefe

                logger.info('JefeSicario ID Inserted: %s', str(jefe_id))

                session.flush()

                data['id_jefe'] = jefe_id

                # check insert correct
                row_inserted = self.get_one_jefe(self, session, data)

                logger.info('Data JefeSicario inserted: %s, Original Data: {}'.format(data), str(row_inserted))

                grupo_sicario = self.get_grupo_sicarios_id(session, data)

                if row_inserted:
                    endpoint_response = json.dumps({
                        "id_jefe": row_inserted.id_jefe,
                        "nombre_jefe": row_inserted.nombre_jefe,
                        "post": grupo_sicario.nombre_grupo
                    })

            except SQLAlchemyError as exc:
                endpoint_response = None
                session.rollback()
                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('cuenta'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    @staticmethod
    def get_history_status_id(session, data):

        row_status = None

        try:

            row_exists = session.query(StatusHistoryModel).\
                filter(StatusHistoryModel.property_id == data.get('property_id')).\
                filter(StatusHistoryModel.status_id == data.get('status_id')).scalar()

            logger.info('Row Data Status Exists on DB: %s', str(row_exists))

            if row_exists:

                row_status = session.query(StatusModel). \
                    filter(StatusHistoryModel.property_id == data.get('property_id')). \
                    filter(StatusHistoryModel.status_id == data.get('status_id')).one()

                logger.info('Row ID Status data from database object: {}'.format(str(row_status)))

        except SQLAlchemyError as exc:

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('property_id'), StatusHistoryModel.__tablename__, str(str(exc.args) + ':' +
                                                                                   str(exc.code))
                )
            )

        finally:
            session.close()

        return row_status

    @staticmethod
    def get_all_history(session):

        all_status_history = None
        status_history_data = []

        all_status_history = session.query(StatusHistoryModel).order_by(StatusHistoryModel.update_date.desc()).all()

        for history in all_status_history:

            history_id = history.id_history
            property_id = history.property_id
            status_id = history.status_id

            status_history_data += [{
                "Status": {
                    "id_status": history_id,
                    "property_id": property_id,
                    "status_id": status_id
                }
            }]

        return json.dumps(status_history_data)

    @staticmethod
    def get_last_status_history(session, data):
        row = None
        status_history_data = []

        try:

            row = StatusHistoryModel.query(StatusHistoryModel). \
                filter(StatusHistoryModel.property_id == data.get('id_property')). \
                filter(StatusHistoryModel.status_id == data.get('id_status')). \
                order_by(StatusHistoryModel.update_date.desc()).all()

            if row:
                logger.info('Data History Status Property on Db: %s',
                            'Property: {}, Status: {}, LastDate: {}'.format(row.property_id,
                                                                            row.status_id,
                                                                            row.update_date))

                for history in row:
                    history_id = history.id_history
                    property_id = history.property_id
                    status_id = history.status_id

                    status_history_data += [{
                        "Status": {
                            "id_status": history_id,
                            "property_id": property_id,
                            "status_id": status_id
                        }
                    }]

                return json.dumps(status_history_data)

        except SQLAlchemyError as exc:
            row = None
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))

            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('id_property'), StatusHistoryModel.__tablename__, str(str(exc.args) + ':' + str(exc.code))
                )
            )

        finally:
            session.close()

    def __repr__(self):
        return "<StatusHistoryModel(id_history='%s', property_id='%s', status_id='%s')>" % \
               (self.id_history, self.property_id, self.status_id)
