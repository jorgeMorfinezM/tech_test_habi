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
from .StatusHistoryModel import StatusHistoryModel
from handler_controller.ResponsesHandler import ResponsesHandler as HandlerResponse
from handler_controller.messages import SuccessMsg, ErrorMsg
from logger_controller.logger_control import *
from utilities.Utility import *
from datetime import datetime

cfg_app = get_config_settings_app()
status_history_api = Blueprint('status_history_api', __name__)
# jwt = JWTManager(bancos_api)
logger = configure_logger('ws')


@status_history_api.route('/', methods=['POST', 'GET'])
@jwt_required
def endpoint_process_history_data():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return HandlerResponse.request_unauthorized()
    else:

        data = dict()

        if request.method == 'POST':
            # Nuevo HistoryStatus a registrar

            history_status_on_db = None

            data = request.get_json(force=True)

            history_status_model = StatusHistoryModel(data)

            if not data or str(data) is None:
                return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

            logger.info('Data Status to Insert on DB: %s', str(data))

            history_status_on_db = history_status_model.insert_data(session_db, data)

            if not history_status_on_db:
                return HandlerResponse.response_success(SuccessMsg.MSG_RECORD_REGISTERED)

            return HandlerResponse.response_resource_created(SuccessMsg.MSG_CREATED_RECORD, history_status_on_db)

        elif request.method == 'GET':
            # To GET ALL Data of the HistoryStatus:

            history_status_on_db = None

            history_status_model = StatusHistoryModel(data)

            history_status_on_db = history_status_model.get_all_history(session_db)

            if not bool(history_status_on_db) or not history_status_on_db or "[]" == history_status_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, {})

            return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, history_status_on_db)

        else:
            return HandlerResponse.request_method_not_allowed(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)


@status_history_api.route('/last/datos', methods=['GET'])
def endpoint_history_datos():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    # auth = headers.get('Authorization')

    # if not auth and 'Bearer' not in auth:
    #     return HandlerResponse.request_unauthorized()
    # else:

    if request.method == 'GET':
        # Obtiene el ultimo registro de estatus en historial de una propiedad

        data = request.get_json(force=True)

        history_status_on_db = None

        history_status_model = StatusHistoryModel(data)

        history_status_on_db = history_status_model.get_last_status_history(session_db, data)

        if not bool(history_status_on_db) or not history_status_on_db or "[]" == history_status_on_db:
            return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, {})

        return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, history_status_on_db)

    else:
        return HandlerResponse.request_method_not_allowed(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)
