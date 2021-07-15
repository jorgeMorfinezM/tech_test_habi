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
from apps.status.StatusModel import StatusModel
from sqlalchemy import desc
from sqlalchemy_filters import apply_filters
from sqlalchemy import Column, Integer, String, Sequence, Float
from db_controller.database_backend import *
from db_controller import mvc_exceptions as mvc_exc

cfg_db = get_config_settings_db()

PROPERTY_ID_SEQ = Sequence('property_id_seq')  # define sequence explicitly


class PropertyModel(Base):
    r"""
    Class to instance the data of VehicleModel on the database.
    Transactions:
     - Insert: Add data to the database if not exists.
     - Update: Update data on the database if exists.
     - Delete:
     - Select:
    """

    __tablename__ = cfg_db.property_table

    id_property = Column('id', Integer, PROPERTY_ID_SEQ, primary_key=True,
                         server_default=PROPERTY_ID_SEQ.next_value())
    address_property = Column('address', String, nullable=False)
    city_property = Column('city', String, nullable=False)
    province_property = Column('province', String, nullable=True)
    price_property = Column('price', Float, nullable=False)
    description_property = Column('description', String, nullable=False)
    year_property = Column('year', Integer, nullable=False)

    def __init__(self, data_property):

        self.address_property = data_property.get('domicilio_propiedad')
        self.city_property = data_property.get('ciudad_propiedad')
        self.province_property = data_property.get('estado_propiedad')
        self.description_property = data_property.get('descripcion_propiedad')
        self.price_property = data_property.get('precio_propiedad')
        self.year_property = data_property.get('anio_construccion')

    def check_if_row_exists(self, session):

        row_exists = None
        id_property = 0
        data = dict()

        try:
            # for example to check if the insert on db is correct
            property_row = self.get_property_id(session, data)

            if property_row is not None:
                id_property = property_row.id_property
            else:
                id_property = 0

            logger.info('Property Row object in DB: %s', str(id_property))

            data['id_property'] = id_property

            row_exists = session.query(PropertyModel).filter(PropertyModel.id_property == id_property).scalar()

            logger.info('Row to data: {}, Exists: %s'.format(data), str(row_exists))

        except SQLAlchemyError as exc:
            row_exists = None
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('id_property'),
                                                                    str(str(exc.args) + ':' + str(exc.code)))
            )
        finally:
            session.close()

        return row_exists

    def insert_data(self, session, data):

        endpoint_response = None

        if not self.check_if_row_exists(session):

            try:

                new_row = PropertyModel(data)

                logger.info('New Row Property: %s', str(new_row.description_property))

                session.add(new_row)

                property_row = self.get_property_id(session, data)

                logger.info('Property ID Inserted: %s', str(property_row.id_property))

                session.flush()

                data['id_property'] = property_row.id_property

                # check insert correct
                row_inserted = self.get_one_property_row(session, data)

                logger.info('Data Sicario inserted: %s, Original Data: {}'.format(data), str(row_inserted))

                if row_inserted:
                    endpoint_response = json.dumps({
                        "Id": row_inserted.id_property,
                        "Domicilio": row_inserted.address_property,
                        "DomicilioEstado": row_inserted.province_property,
                        "DomicilioCiudad": row_inserted.city_property,
                        "Precio": str(row_inserted.price_property),
                        "Descripcion": row_inserted.description_property,
                        "AnioConstruccion": row_inserted.year_property
                    })

            except SQLAlchemyError as exc:
                endpoint_response = None
                session.rollback()
                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('descripcion_propiedad'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    def update_data(self, session, data):

        endpoint_response = None

        if self.check_if_row_exists(session):

            try:

                property_row = self.get_property_id(session, data)

                # update row to database
                session.query(PropertyModel).filter(PropertyModel.id_property == property_row.id_property). \
                    update({"address_property": data.get('domicilio_propiedad'),
                            "city_property": data.get('ciudad_propiedad'),
                            "province_property": data.get('estado_propiedad'),
                            "price_property": data.get('precio_propiedad'),
                            "description_property": data.get('descripcion_propiedad'),
                            "year_property": data.get('anio_construccion')},
                           synchronize_session='fetch')

                session.flush()

                data['id_property'] = property_row.id_property

                # check update correct
                row_updated = self.get_one_property_row(session, data)

                logger.info('Data Updated: %s', str(row_updated))

                if row_updated:
                    logger.info('Data Property updated')

                    endpoint_response = json.dumps({
                        "Id": row_updated.id_property,
                        "Domicilio": row_updated.address_property,
                        "DomicilioEstado": row_updated.province_property,
                        "DomicilioCiudad": row_updated.city_property,
                        "Precio": str(row_updated.price_property),
                        "Descripcion": row_updated.description_property,
                        "AnioConstruccion": row_updated.year_property
                    })

            except SQLAlchemyError as exc:
                endpoint_response = None
                session.rollback()
                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('descripcion_propiedad'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    def delete_data(self, session, data):

        endpoint_response = None

        try:

            property_row = self.get_property_id(session, data)

            logger.info('Property Id: %s', str(property_row.id_property))

            session.query(PropertyModel).filter(PropertyModel.id_property == property_row.id_property).delete()

            session.flush()

            data['id_property'] = property_row.id_property

            # check update correct
            row_deleted = self.get_one_property_row(session, data)

            if row_deleted:
                logger.info('Property deleted')

                endpoint_response = json.dumps({
                    "Id": property_row.id_property,
                    "Domicilio": property_row.address_property,
                    "DomicilioEstado": property_row.province_property,
                    "DomicilioCiudad": property_row.city_property,
                    "Precio": str(property_row.price_property),
                    "Descripcion": property_row.description_property,
                    "AnioConstruccion": property_row.year_property
                })

        except SQLAlchemyError as exc:
            endpoint_response = None
            session.rollback()
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('id_property'),
                                                                    str(str(exc.args) + ':' + str(exc.code)))
            )
        finally:
            session.close()

        return endpoint_response

    @staticmethod
    def get_property_id(session, data):

        row_property = None

        try:

            row_exists = session.query(PropertyModel).\
                filter(PropertyModel.price_property == data.get('price_property')).\
                filter(PropertyModel.city_property == data.get('city_property')).\
                filter(PropertyModel.year_property == data.get('year_property')).scalar()

            logger.info('Row Data Property Exists on DB: %s', str(row_exists))

            if row_exists:

                row_property = session.query(PropertyModel).\
                    filter(PropertyModel.price_property == data.get('price_property')).\
                    filter(PropertyModel.city_property == data.get('city_property')).\
                    filter(PropertyModel.year_property == data.get('year_property')).one()

                logger.info('Row ID Property data from database object: {}'.format(str(row_property)))

        except SQLAlchemyError as exc:

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('city_property'), PropertyModel.__tablename__, str(str(exc.args) + ':' +
                                                                                str(exc.code))
                )
            )

        finally:
            session.close()

        return row_property

    @staticmethod
    def get_one_property_row(session, data):
        row = None

        try:
            row = session.query(PropertyModel).filter(PropertyModel.id_property == data.get('id_property')).one()

            if row:
                logger.info('Data Property on Db: %s',
                            'Description: {}, Price: {}, City: {}'.format(row.description_property,
                                                                          row.price_property,
                                                                          row.city_property))

        except SQLAlchemyError as exc:

            row = None

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))

            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('id_property'), PropertyModel.__tablename__, str(str(exc.args) + ':' + str(exc.code))
                )
            )

        finally:
            session.close()

        return row

    @staticmethod
    def get_all_properties(session):

        all_properties = None
        property_data = []
        data = dict()

        all_properties = session.query(PropertyModel).all()

        for property_rs in all_properties:

            id_property = property_rs.id_property
            address_property = property_rs.address_property
            city_property = property_rs.city_property
            province_property = property_rs.province_property
            price_property = property_rs.price_property
            description_property = property_rs.description_property
            year_build = property_rs.year_property

            property_data += [{
                "Propiedad": {
                    "Id": id_property,
                    "Domicilio": address_property,
                    "DomicilioEstado": province_property,
                    "DomicilioCiudad": city_property,
                    "Precio": str(price_property),
                    "Descripcion": description_property,
                    "AnioConstruccion": year_build
                }
            }]

        return json.dumps(property_data)

    @staticmethod
    def get_properties_by_filters(session, filter_spec_prop, filter_spec_status):

        from apps.status_history.StatusHistoryModel import StatusHistoryModel

        query = None
        query_result_prop = None
        query_result_status = None
        query_result = None
        property_data = []

        if filter_spec_prop is None:
            query_result_prop = session.query(PropertyModel).all()

        if type(filter_spec_prop) == tuple:
            query = session.query(PropertyModel).filter(*filter_spec_prop)
        elif type(filter_spec_prop) == dict:
            query = session.query(PropertyModel).filter(**filter_spec_prop)

        # query = session.query(PropertyModel)

        filtered_query = apply_filters(session.query(PropertyModel).all(), filter_spec_prop)
        query_result_prop = filtered_query.all()
        # query_result_prop = query.all()

        logger.info('Query filtered Property resultSet: %s', str(query_result_prop))

        if query_result_prop:

            for property_rs in query_result_prop:

                id_property = property_rs.id_property

                query_result_status = session.query(StatusModel).all()

                id_status = str()

                if filter_spec_status is not None:
                    query_status = session.query(StatusModel)

                    filtered_query_status = apply_filters(query_status, filter_spec_status)
                    query_result_status = filtered_query_status.all()

                    for status_prop in query_result_status:
                        id_status = status_prop.id_status
                        # status_name = status_prop.name_status
                        # status_label = status_prop.label_status

                # entities = StatusHistoryModel.query.order_by(desc(StatusHistoryModel.update_date)).one()
                query_result = StatusHistoryModel.query(StatusHistoryModel).\
                    filter(StatusHistoryModel.property_id == id_property).\
                    filter(StatusHistoryModel.status_id == id_status).\
                    order_by(StatusHistoryModel.update_date.desc()).all()

                for property_search in query_result:

                    address_property = property_search.address_property
                    city_property = property_search.city_property
                    province_property = property_search.province_property
                    price_property = property_search.price_property
                    description_property = property_search.description_property

                    property_data += [{
                        "Propiedad": {
                            "Domicilio": address_property,
                            "DomicilioEstado": province_property,
                            "DomicilioCiudad": city_property,
                            "Precio": str(price_property),
                            "Descripcion": description_property
                        }
                    }]

            return json.dumps(property_data)

    def __repr__(self):
        return "<PropertyModel(" \
               "id_property='%s', " \
               "address_property='%s', " \
               "city_property='%s', " \
               "province_property='%s'," \
               "price_property='%s', " \
               "description_property='%s'," \
               "year_property='%s')>" % (self.id_property,
                                         self.address_property,
                                         self.city_property,
                                         self.province_property,
                                         self.price_property,
                                         self.description_property,
                                         self.year_property
        )
