# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021"
__license__ = ""
__history__ = """ """
__version__ = "1.21.G02.1 ($Rev: 2 $)"

from flask import Blueprint, json, request
from flask_jwt_extended import jwt_required
from db_controller.database_backend import *
from .PropertyModel import PropertyModel
from handler_controller.ResponsesHandler import ResponsesHandler as HandlerResponse
from handler_controller.messages import SuccessMsg, ErrorMsg
from logger_controller.logger_control import *
from utilities.Utility import *
from datetime import datetime

cfg_app = get_config_settings_app()
property_api = Blueprint('property_api', __name__)
# jwt = JWTManager(bancos_api)
logger = configure_logger('ws')


@property_api.route('/', methods=['POST', 'PUT', 'GET', 'DELETE'])
@jwt_required
def endpoint_processing_properties_data():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return HandlerResponse.request_unauthorized(ErrorMsg.ERROR_REQUEST_UNAUTHORIZED)
    else:

        data = dict()

        if request.method == 'POST':
            # Insertar datos de una propiedad

            data = request.get_json(force=True)

            property_model = PropertyModel(data)

            if not data or str(data) is None:
                return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

            logger.info('Data Property to Insert on DB: %s', str(data))

            json_property_added = property_model.insert_data(session_db, data)

            if not json_property_added:
                return HandlerResponse.response_success(SuccessMsg.MSG_RECORD_REGISTERED)

            return HandlerResponse.response_resource_created(SuccessMsg.MSG_CREATED_RECORD, json_property_added)

        elif request.method == 'PUT':
            # Actualizar datos de una propiedad

            data = request.get_json(force=True)

            property_model = PropertyModel(data)

            if not data or str(data) is None:
                return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

            json_property_updated = property_model.update_data(session_db, data)

            logger.info('Property updated Info: %s', str(json_property_updated))

            if not json_property_updated:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND)

            return HandlerResponse.response_success(SuccessMsg.MSG_UPDATED_RECORD, json_property_updated)

        elif request.method == 'GET':
            # To GET ALL Data of the Properties:

            properties_on_db = None

            property_model = PropertyModel(data)

            properties_on_db = property_model.get_all_properties(session_db)

            if not bool(properties_on_db) or not properties_on_db or "[]" == properties_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, {})

            return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, properties_on_db)

        elif request.method == 'DELETE':

            property_model = PropertyModel(data)

            if not data or str(data) is None:
                return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

            json_property_deleted = property_model.delete_data(session_db, data)

            logger.info('Property deleted: %s', json_property_deleted)

            if not json_property_deleted:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND)

            return HandlerResponse.response_success(SuccessMsg.MSG_DELETED_RECORD, json_property_deleted)

        else:
            return HandlerResponse.request_method_not_allowed(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)


@property_api.route('/filter', methods=['GET'])
def endpoint_flujo_datos():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    # auth = headers.get('Authorization')

    # if not auth and 'Bearer' not in auth:
    #     return HandlerResponse.request_unauthorized()
    # else:

    try:
        uploaded_file = request.files['archivo']

    except IOError as io_error:

        return HandlerResponse.bad_request(ErrorMsg.ERROR_FILE_IS_NEEDED)

    filter_json_object = get_filter_property_file(uploaded_file)

    query_string = make_query_string_filters(filter_json_object)  # Para obtener datos del archivo cargado al endpoint

    # query_string = request.query_string.decode('utf-8')  # En el caso que se tomen datos de variables del endpoint

    if request.method == 'GET':
        # Obtiene los datos de las propiedades por filtro

        data = dict()
        properties_filter = None

        status_property = None
        build_year = None
        city_address = None
        province_address = None
        filter_spec_prop = []
        filter_spec_status = []

        status_allowed = ['pre_venta', 'en_venta', 'vendido']

        if 'estatus' in query_string:
            # status_property = request.args.get('estatus')
            status_property = '{}'.format(filter_json_object['estatus'])

            data['estatus'] = status_property

            if status_property.lower() in status_allowed:

                filter_spec_status.append({'field': 'name_status', 'op': 'ilike', 'value': status_property})

        if 'anio_construccion' in query_string:
            # build_year = request.args.get('anio_construccion')
            build_year = '{}'.format(filter_json_object['anio_construccion'])

            data['anio_construccion'] = build_year

            filter_spec_prop.append({'field': 'year', 'op': 'eq', 'value': build_year})

        if 'ciudad_propiedad' in query_string:
            # city_address = request.args.get('ciudad_propiedad')
            city_address = '{}'.format(filter_json_object['ciudad_propiedad'])

            data['ciudad_propiedad'] = city_address

            filter_spec_prop.append({'field': 'city', 'op': 'ilike', 'value': city_address})

        if 'estado_propiedad' in query_string:
            # province_address = request.args.get('estado_propiedad')
            province_address = '{}'.format(filter_json_object['estado_propiedad'])

            data['estado_propiedad'] = province_address

            filter_spec_prop.append({'field': 'province', 'op': 'ilike', 'value': province_address})

        property_obj = PropertyModel(data)

        properties_filter = property_obj.get_properties_by_filters(session_db, filter_spec_prop, filter_spec_status)

        logger.info('Query filtered resultSet: %s', str(properties_filter))

        if not bool(properties_filter) or not properties_filter or "[]" == properties_filter:
            return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND)

        return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, properties_filter)

    else:
        return HandlerResponse.request_method_not_allowed(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)
