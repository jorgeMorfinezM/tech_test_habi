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
from .StatusModel import StatusModel
from handler_controller.ResponsesHandler import ResponsesHandler as HandlerResponse
from handler_controller.messages import SuccessMsg, ErrorMsg
from logger_controller.logger_control import *
from utilities.Utility import *
from datetime import datetime

cfg_app = get_config_settings_app()
status_api = Blueprint('status_api', __name__)
logger = configure_logger('ws')


@status_api.route('/', methods=['POST', 'PUT', 'GET', 'DELETE'])
@jwt_required
def endpoint_process_status_data():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return HandlerResponse.request_unauthorized()
    else:

        data = dict()

        if request.method == 'POST':
            # Nuevo Status a registrar

            status_on_db = None

            data = request.get_json(force=True)

            status_model = StatusModel(data)

            if not data or str(data) is None:
                return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

            logger.info('Data Status to Insert on DB: %s', str(data))

            status_on_db = status_model.insert_data(session_db, data)

            if not status_on_db:
                return HandlerResponse.response_success(SuccessMsg.MSG_RECORD_REGISTERED)

            return HandlerResponse.response_resource_created(SuccessMsg.MSG_CREATED_RECORD, status_on_db)

        elif request.method == 'PUT':

            data = request.get_json(force=True)

            status_on_db = None

            status_model = StatusModel(data)

            if not data or str(data) is None:
                return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

            status_on_db = status_model.update_data(session_db, data)

            logger.info('Status updated Info: %s', str(status_on_db))

            if not status_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND)

            return HandlerResponse.response_success(SuccessMsg.MSG_UPDATED_RECORD, status_on_db)

        elif request.method == 'GET':
            # To GET ALL Data of the Status:

            status_on_db = None

            status_model = StatusModel(data)

            status_on_db = status_model.get_all_status(session_db)

            if not bool(status_on_db) or not status_on_db or "[]" == status_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, {})

            return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, status_on_db)

        elif request.method == 'DELETE':

            data = request.get_json(force=True)

            status_model = StatusModel(data)

            if not data or str(data) is None:
                return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

            json_status_deleted = status_model.delete_data(session_db, data)

            logger.info('Status deleted: %s', json_status_deleted)

            if not json_status_deleted:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND)

            return HandlerResponse.response_success(SuccessMsg.MSG_DELETED_RECORD, json_status_deleted)

        else:
            return HandlerResponse.request_method_not_allowed(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)
