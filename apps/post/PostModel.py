# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later


PostgreSQL DB backend.

Each one of the CRUD operations should be able to open a database connection if
there isn't already one available (check if there are any issues with this).

Documentation:
    About the Grupo Sicario data on the database to generate CRUD operations from endpoint of the API:
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
from sqlalchemy import Column, Numeric, Integer, String, Date, Time, Sequence
from db_controller.database_backend import *
from db_controller import mvc_exceptions as mvc_exc

cfg_db = get_config_settings_db()

GRUPO_SICARIOS_ID_SEQ = Sequence('grupo_sicarios_seq')  # define sequence explicitly


class PostModel(Base):

    r"""
    Class to instance the data of DriverModel on the database.
    Transactions:
     - Insert: Add data to the database if not exists.
     - Update: Update data on the database if exists.
     - Delete:
     - Select:
    """

    __tablename__ = cfg_db.grupo_sicarios_table

    id_grupo = Column('id_grupo', Integer, GRUPO_SICARIOS_ID_SEQ, primary_key=True,
                      server_default=GRUPO_SICARIOS_ID_SEQ.next_value())
    nombre_grupo = Column('nombre_grupo', String, nullable=False)

    def __init__(self, data_grupo):
        self.nombre_grupo = data_grupo.get('nombre_grupo')

    def check_if_row_exists(self, session, data):

        row_exists = None
        grupo_id = 0

        try:
            # for example to check if the insert on db is correct
            id_grupo = self.get_grupo_id(session, data)

            if id_grupo is not None:
                grupo_id = id_grupo.id_grupo

            logger.info('GrupoSicario Row object in DB: %s', str(grupo_id))

            row_exists = session.query(GrupoSicarioModel).filter(GrupoSicarioModel.id_grupo == grupo_id).\
                filter(GrupoSicarioModel.nombre_grupo == data.get('nombre_grupo')).scalar()

            logger.info('Row to data: {}, Exists: %s'.format(data), str(row_exists))

        except SQLAlchemyError as exc:
            row_exists = None

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre_grupo'),
                                                                    str(str(exc.args) + ':' + str(exc.code)))
            )
        finally:
            session.close()

        return row_exists

    def insert_data(self, session, data):

        endpoint_response = None

        if not self.check_if_row_exists(session, data):

            try:

                new_row = GrupoSicarioModel(data)

                logger.info('New Row GrupoSicaario: %s', str(new_row.nombre_grupo))

                session.add(new_row)

                id_grupo = self.get_grupo_id(session, data).id_grupo

                logger.info('GrupoSicario ID Inserted: %s', str(id_grupo))

                session.flush()

                data['id_grupo'] = id_grupo

                # check insert correct
                row_inserted = self.get_one_grupo(session, data)

                logger.info('Data GrupoSicarios inserted: %s, Original Data: {}'.format(data), str(row_inserted))

                if row_inserted:
                    endpoint_response = json.dumps({
                        "id_grupo": id_grupo,
                        "nombre_grupo": row_inserted.nombre_grupo
                    })

            except SQLAlchemyError as exc:

                endpoint_response = None

                session.rollback()

                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre_grupo'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    def update_data(self, session, data):

        if self.check_if_row_exists(session, data):

            try:

                id_grupo = self.get_grupo_id(session, data).id_grupo

                # update row to database
                session.query(GrupoSicarioModel).filter(GrupoSicarioModel.id_grupo == id_grupo).\
                    update({"nombre_grupo": data.get('nombre_grupo')},
                           synchronize_session='fetch')

                session.flush()

                data['id_grupo'] = id_grupo

                # check update correct
                row_updated = self.get_one_grupo(session, data)

                logger.info('Data Updated: %s', str(row_updated))

                if row_updated:
                    logger.info('Data GrupoSicario updated')

                    return json.dumps({
                        "id_grupo": row_updated.id_grupo,
                        "nombre_grupo": row_updated.nombre_grupo
                    })

            except SQLAlchemyError as exc:
                session.rollback()
                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre_grupo'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

    @staticmethod
    def get_grupo_id(session, data):

        row_grupo = None

        try:

            row_exists = session.query(GrupoSicarioModel).\
                filter(GrupoSicarioModel.nombre_grupo == data.get('nombre_grupo')).scalar()

            logger.info('Row GrupoSicario Exists on DB: %s', str(row_exists))

            if row_exists:

                row_grupo = session.query(GrupoSicarioModel).\
                    filter(GrupoSicarioModel.nombre_grupo == data.get('nombre_grupo')).one()

                logger.info('Row ID GrupoSicario data from database object: {}'.format(str(row_grupo)))

        except SQLAlchemyError as exc:

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('nombre_grupo'), GrupoSicarioModel.__tablename__, str(str(exc.args) + ':' +
                                                                                    str(exc.code))
                )
            )

        finally:
            session.close()

        return row_grupo

    @staticmethod
    def get_all_grupos(session):

        all_inversiones = None
        grupos_data = []

        all_grupos = session.query(GrupoSicarioModel).all()

        for grupo in all_grupos:

            id_grupo = grupo.id_grupo
            nombre_grupo = grupo.nombre_grupo

            grupos_data += [{
                "GrupoSicaario": {
                    "id_grupo": id_grupo,
                    "nombre_grupo": nombre_grupo
                }
            }]

        return json.dumps(grupos_data)

    @staticmethod
    def get_one_grupo(session, data):
        row = None

        try:
            row = session.query(GrupoSicarioModel).filter(GrupoSicarioModel.nombre_grupo == data.get('nombre_grupo')).\
                filter(GrupoSicarioModel.id_grupo == data.get('id_grupo')).one()

            if row:
                logger.info('Data GrupoSicarios on Db: %s',
                            'IdGrupo: {}, Nombre Grupo: {}'.format(row.id_grupo, row.nombre_grupo))

        except SQLAlchemyError as exc:

            row = None

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))

            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('nombre_grupo'), GrupoSicarioModel.__tablename__, str(str(exc.args) + ':' + str(exc.code))
                )
            )

        finally:
            session.close()

        return row

    def __repr__(self):
        return "<GrupoSicarioModel(id_grupo='%s', nombre_grupo='%s')>" % (self.id_grupo, self.nombre_grupo)

    # @staticmethod
    # def get_inversiones_by_filters(session, filter_spec=list):
    #
    #     query_result = None
    #     inversiones_data = []
    #
    #     if filter_spec is None:
    #         query_result = session.query(GinInversionesModel).all()
    #
    #     query = session.query(GinInversionesModel)
    #
    #     filtered_query = apply_filters(query, filter_spec)
    #     query_result = filtered_query.all()
    #
    #     logger.info('Query filtered resultSet: %s', str(query_result))
    #
    #     for inversion in query_result:
    #         inversion_id = inversion.invId
    #         cuenta = inversion.cuenta
    #         estatus = inversion.estatus
    #         monto = inversion.monto
    #         autorizacion = inversion.autorizacion
    #         canal = inversion.canal
    #         origen = inversion.origen
    #         comisionistaId = inversion.comisionistaId
    #         transaccionId = inversion.transaccionId
    #         motivo = inversion.motivo
    #         fechaRecepcion = inversion.fechaRecepcion
    #         horaRecepcion = inversion.horaRecepcion
    #         fechaAplicacion = inversion.fechaAplicacion
    #         horaAplicacion = inversion.horaAplicacion
    #         conciliacionId = inversion.conciliacionId
    #         codigoBancario = inversion.codigoBancario
    #         metodoDeposito = inversion.metodoDeposito
    #
    #         inversiones_data += [{
    #             "invId": inversion_id,
    #             "cuenta": cuenta,
    #             "estatus": estatus,
    #             "monto": str(monto),
    #             "autorizacion": autorizacion,
    #             "canal": canal,
    #             "origen": origen,
    #             "comisionistaId": comisionistaId,
    #             "transaccionId": transaccionId,
    #             "motivo": motivo,
    #             "fechaRecepcion": str(fechaRecepcion),
    #             "horaRecepcion": str(horaRecepcion),
    #             "fechaAplicacion": str(fechaAplicacion),
    #             "horaAplicacion": str(horaAplicacion),
    #             "conciliacionId": conciliacionId,
    #             "codigoBancario": codigoBancario,
    #             "metodoDeposito": metodoDeposito
    #         }]
    #
    #     return json.dumps(inversiones_data)
