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
from apps.property.PropertyModel import PropertyModel
from apps.status.StatusModel import StatusModel
from sqlalchemy_filters import apply_filters
from sqlalchemy import Column, Numeric, Integer, String, Date, Time, Sequence, Float
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
        # self.update_date = get_current_date(session)  # SI VA pero en el metodo insert

    def check_if_row_exists(self, session, data):

        row_exists = None
        inversion_id = 0

        try:
            # for example to check if the insert on db is correct
            jefe_id = self.get_status_id(session, data)

            if jefe_id is not None:
                id_jefe = jefe_id.id_jefe
            else:
                id_jefe = 0

            logger.info('Jefe Sicario Row object in DB: %s', str(id_jefe))

            row_exists = session.query(JefeSicarioModel).filter(JefeSicarioModel.id_jefe == id_jefe).scalar()

            logger.info('Row to data: {}, Exists: %s'.format(data), str(row_exists))

        except SQLAlchemyError as exc:
            row_exists = None

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('cuenta'),
                                                                    str(str(exc.args) + ':' + str(exc.code)))
            )
        finally:
            session.close()

        return row_exists

    def insert_data(self, session, data):

        endpoint_response = None

        if not self.check_if_row_exists(session, data):

            try:

                new_row = JefeSicarioModel(data)

                logger.info('New Row JefeSicario: %s', str(new_row.nombre_jefe))

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
                        "like": grupo_sicario.nombre_grupo
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

    def update_data(self, session, data):

        endpoint_response = None

        if self.check_if_row_exists(session, data):

            try:

                jefe_id = self.get_status_id(session, data).id_jefe

                grupo_sicario = self.get_grupo_sicarios_id(session, data)

                # update row to database
                session.query(JefeSicarioModel).filter(JefeSicarioModel.id_jefe == jefe_id).\
                    update({"nombre_jefe": data.get('nombre_jefe'),
                            "id_grupo_sicario": data.get('like')},
                           synchronize_session='fetch')

                session.flush()

                data['like'] = grupo_sicario.id_grupo
                data['id_jefe'] = jefe_id

                # check update correct
                row_updated = self.get_one_jefe(self, session, data)

                logger.info('Data Updated: %s', str(row_updated))

                if row_updated:
                    logger.info('Data JefeSicario updated')

                    endpoint_response = json.dumps({
                        "id_jefe": row_updated.id_jefe,
                        "nombre_jefe": row_updated.nombre_jefe,
                        "like": grupo_sicario.nombre_grupo
                    })

            except SQLAlchemyError as exc:
                endpoint_response = None
                session.rollback()
                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre_jefe'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    def delete_data(self, session, data):

        endpoint_response = None

        try:

            jefe_id = self.get_status_id(session, data).id_jefe

            grupo_sicario = self.get_grupo_sicarios_id(session, data)

            logger.info('JefeSicario Id: %s', str(jefe_id))

            session.query(JefeSicarioModel).filter(JefeSicarioModel.id_jefe == jefe_id).delete()

            session.flush()

            data['id_jefe'] = jefe_id

            # check update correct
            row_deleted = self.get_one_jefe(self, session, data)

            if not row_deleted or row_deleted is None:
                logger.info('JefeSicario inactive')

                endpoint_response = json.dumps({
                    "id_jefe": jefe_id,
                    "nombre_jefe": data.get('nombre_jefe'),
                    "grupo_sicarios": grupo_sicario.nombre_grupo
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

    @staticmethod
    def get_grupo_sicarios_id(session, data):

        row_grupo = None

        try:

            row_exists = session.query(GrupoSicarioModel). \
                filter(GrupoSicarioModel.id_grupo == data.get('like')).scalar()

            logger.info('Row GrupoSicario Exists on DB: %s', str(row_exists))

            if row_exists:
                row_grupo = session.query(GrupoSicarioModel). \
                    filter(GrupoSicarioModel.id_grupo == data.get('like')).one()

                logger.info('Row ID GrupoSicario data from database object: {}'.format(str(row_grupo)))

        except SQLAlchemyError as exc:

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('like'), GrupoSicarioModel.__tablename__, str(str(exc.args) + ':' +
                                                                                    str(exc.code))
                )
            )

        finally:
            session.close()

        return row_grupo

    @staticmethod
    def get_all_jefes(session):

        all_jefes = None
        jefes_data = []

        all_jefes = session.query(JefeSicarioModel).all()

        for jefe in all_jefes:

            jefe_id = jefe.id_jefe
            nombre_jefe = jefe.nombre_jefe
            id_grupo_sicario = jefe.id_grupo_sicario

            jefes_data += [{
                "Jefe": {
                    "id_jefe": jefe_id,
                    "cuenta": nombre_jefe,
                    "like": id_grupo_sicario
                }
            }]

        return json.dumps(jefes_data)

    @staticmethod
    def get_one_jefe(self, session, data):
        row = None

        try:
            id_jefe = self.get_status_id(session, data).id_jefe

            row = session.query(JefeSicarioModel).filter(JefeSicarioModel.nombre_jefe == data.get('nombre_jefe')).\
                filter(JefeSicarioModel.id_jefe == id_jefe).one()

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
                    data.get('nombre_jefe'), JefeSicarioModel.__tablename__, str(str(exc.args) + ':' + str(exc.code))
                )
            )

        finally:
            session.close()

        return row

    def __repr__(self):
        return "<JefeSicarioModel(id_jefe='%s', nombre_jefe='%s', id_grupo_sicario='%s')>" % \
               (self.id_jefe, self.nombre_jefe, self.id_grupo_sicario)
