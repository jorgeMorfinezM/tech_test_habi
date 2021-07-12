# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021"
__license__ = ""
__history__ = """ """
__version__ = "1.21.G02.1 ($Rev: 2 $)"

import re
from flask import Blueprint, json, request, render_template
from flask_jwt_extended import jwt_required
from db_controller.database_backend import *
from .AuthUserModel import AuthUserModel
from handler_controller.ResponsesHandler import ResponsesHandler as HandlerResponse
from handler_controller.messages import SuccessMsg, ErrorMsg
from auth_controller.api_authentication import *
from logger_controller.logger_control import *
from utilities.Utility import *
from datetime import datetime

cfg_app = get_config_settings_app()
user_auth_api = Blueprint('user_auth_api', __name__)
# jwt = JWTManager(bancos_api)
logger = configure_logger('ws')


# Contiene la llamada al HTML que soporta la documentacion de la API,
# sus metodos, y endpoints con los modelos de datos I/O
@user_auth_api.route('/api/v1/manager/')
def main():
    return render_template('api_property_manager.html')


@user_auth_api.route('/', methods=['PUT', 'PATCH', 'GET', 'DELETE'])
# @jwt_required
def endpoint_process_user_data():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    # auth = headers.get('Authorization')

    # if not auth and 'Bearer' not in auth:
    #     return HandlerResponse.request_unauthorized()
    # else:

    data = dict()

    if request.method in ('PUT', 'PATCH'):
        # Actualizar datos de Usuarios

        json_user_updated = None

        data = request.get_json(force=True)

        user_model = AuthUserModel(data)

        if not data or str(data) is None:
            return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

        if not data or str(data) is None:
            return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

        user_name = data['username']
        password = data['password']
        email = data['email']
        # rfc = data['rfc_client']

        regex_email = r"^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$"

        regex_passwd = r"^[(A-Za-z0-9\_\-\.\$\#\&\*)(A-Za-z0-9\_\-\.\$\#\&\*)]+"

        # regex_rfc = r
        # "^([A-ZÑ&]{3,4})?(?:-?)?(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01]))?(?:-?)?([A-Z\d]{2})([A\d])$"

        match_email = re.match(regex_email, email, re.M | re.I)

        match_passwd = re.match(regex_passwd, password, re.M | re.I)

        # match_rfc = re.match(regex_rfc, rfc, re.M | re.I)

        if match_email and match_passwd:
            password = password + '_' + cfg_app.api_key + '_' + email

            password_hash = generate_hash(password)

            data['username'] = user_name
            data['password'] = password_hash

            if request.method == 'PUT':
                json_user_updated = user_model.update_data(session_db, data)
            elif request.method == 'PATCH':
                json_user_updated = user_model.user_update_password(session_db, data)

        else:
            return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

        logger.info('User updated Info: %s', str(json_user_updated))

        if not json_user_updated:
            return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND)

        return HandlerResponse.response_success(SuccessMsg.MSG_UPDATED_RECORD, json_user_updated)

    elif request.method == 'GET':
        # To GET ALL Data of the Users:

        users_on_db = None

        user_model = AuthUserModel(data)

        users_on_db = user_model.get_all_users(session_db)

        if not bool(users_on_db) or not users_on_db or "[]" == users_on_db:
            return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, {})

        return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, users_on_db)

    elif request.method == 'DELETE':

        user_model = AuthUserModel(data)

        if not data or str(data) is None:
            return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

        json_user_deleted = user_model.delete_data(session_db, data)

        logger.info('User deleted: %s', json_user_deleted)

        if not json_user_deleted:
            return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND)

        return HandlerResponse.response_success(SuccessMsg.MSG_DELETED_RECORD, json_user_deleted)

    else:
        return HandlerResponse.request_method_not_allowed(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)


@user_auth_api.route('/register/', methods=['POST'])
def get_authentication():
    conn_db, session_db = init_db_connection()

    data = dict()
    json_token = dict()

    if request.method == 'POST':
        # Insertar/Registrar datos de un Usuario y obtener el Token de autenticacion

        data = request.get_json(force=True)

        if not data or str(data) is None:
            return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

        user_name = data['username']
        password = data['password']
        email = data['email']
        # rfc = data['rfc_client']

        regex_email = r"^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$"

        regex_passwd = r"^[(A-Za-z0-9\_\-\.\$\#\&\*)(A-Za-z0-9\_\-\.\$\#\&\*)]+"

        # regex_rfc = r
        # "^([A-ZÑ&]{3,4})?(?:-?)?(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01]))?(?:-?)?([A-Z\d]{2})([A\d])$"

        match_email = re.match(regex_email, email, re.M | re.I)

        match_passwd = re.match(regex_passwd, password, re.M | re.I)

        # match_rfc = re.match(regex_rfc, rfc, re.M | re.I)

        if match_email and match_passwd:
            password = password + '_' + cfg_app.api_key + '_' + email

            password_hash = generate_hash(password)

            data['username'] = user_name
            data['password'] = password
            data['password_hash'] = password_hash

            json_token = json.dumps(user_registration(session_db, data))

        else:
            return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

        logger.info('Data User to Register on DB: %s', str(data))

        if not json_token:
            return HandlerResponse.response_success(SuccessMsg.MSG_RECORD_REGISTERED)

        return HandlerResponse.response_resource_created(SuccessMsg.MSG_CREATED_RECORD, json_token)

    else:
        return HandlerResponse.request_not_found()
