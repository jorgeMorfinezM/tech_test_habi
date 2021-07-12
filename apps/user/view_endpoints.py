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
# from flask_jwt_extended import jwt_required
from db_controller.database_backend import *
from .AuthUserModel import AuthUserModel
from handler_controller.ResponsesHandler import ResponsesHandler as HandlerResponse
from handler_controller.messages import SuccessMsg, ErrorMsg
from auth_controller.api_authentication import *
from logger_controller.logger_control import *
from utilities.Utility import *
from datetime import datetime

cfg_app = get_config_settings_app()
inversiones_api = Blueprint('inversiones_api', __name__)
# jwt = JWTManager(bancos_api)
logger = configure_logger('ws')


authorization_api = Blueprint('authorization_api', __name__)


# Se inicializa la App con un hilo para evitar problemas de ejecucion
@app.before_first_request
def activate_job():
    def run_job():
        while True:
            time.sleep(2)

    thread = threading.Thread(target=run_job)
    thread.start()


# Contiene la llamada al HTML que soporta la documentacion de la API,
# sus metodos, y endpoints con los modelos de datos I/O
@authorization_api.route('/')
def main():
    return render_template('api_gas_manager.html')


@inversiones_api.route('/', methods=['POST', 'GET', 'DELETE'])
# @jwt_required
def endpoint_processing_inversiones_data():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    # auth = headers.get('Authorization')

    # if not auth and 'Bearer' not in auth:
    #     return HandlerResponse.request_unauthorized()
    # else:

    query_string = request.query_string.decode('utf-8')

    if request.method == 'POST':
        # APLICAR INVERSIONES

        data = request.get_json(force=True)

        gin_inv_model = GinInversionesModel(data)

        if not data or str(data) is None:
            return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

        logger.info('Data Json Inversion to Manage on DB: %s', str(data))

        fechaRecepcion = str()
        horaRecepcion = str()
        fechaAplicacion = str()
        horaAplicacion = str()

        fecha_recepcion = data.get('fechaRecepcion')
        hora_recepcion = data.get('horaRecepcion')

        if fecha_recepcion and hora_recepcion:
            fecha_hora_recepcion = str(datetime.strptime(str(fecha_recepcion), "%Y-%m-%d")) + " " + \
                                   str(datetime.strptime(str(hora_recepcion), "%H:%M:%S"))

            fechaRecepcion, horaRecepcion = set_utc_date_data(fecha_hora_recepcion, cfg_app.date_timezone)

        fecha_aplicacion = data.get('fechaAplicacion')
        hora_aplicacion = data.get('horaAplicacion')

        if fecha_aplicacion and hora_aplicacion:
            fecha_hora_aplicacion = str(datetime.strptime(str(fecha_aplicacion), "%Y-%m-%d")) + " " + \
                                   str(datetime.strptime(str(hora_aplicacion), "%H:%M:%S"))

            fechaAplicacion, horaAplicacion = set_utc_date_data(fecha_hora_aplicacion, cfg_app.date_timezone)

        data_insert = {
            'cuenta': data.get('cuenta'),
            'estatus': data.get('estatus'),
            'monto': data.get('monto'),
            'autorizacion': data.get('autorizacion'),
            'canal': data.get('canal'),
            'origen': data.get('origen'),
            'comisionistaId': data.get('comisionistaId'),
            'transaccionId': data.get('transaccionId'),
            'motivo': data.get('motivo'),
            'fechaRecepcion': fechaRecepcion,
            'horaRecepcion': horaRecepcion,
            'fechaAplicacion': fechaAplicacion,
            'horaAplicacion': horaAplicacion,
            'conciliacionId': data.get('conciliacionId')
        }

        json_bank_added = gin_inv_model.insert_data(session_db, data_insert)

        if not json_bank_added:
            return HandlerResponse.resp_success(SuccessMsg.MSG_RECORD_REGISTERED, {})

        return HandlerResponse.resp_success(SuccessMsg.MSG_CREATED_RECORD, json_bank_added)

    elif request.method == 'GET':
        # To GET ALL Data of the Banks:

        data = dict()
        inversiones_on_db = None

        filter_spec = []

        if 'canal' in query_string:
            canal = request.args.get('canal')

            data['canal'] = canal

            filter_spec.append({'field': 'canal', 'op': '==', 'value': canal})

        if 'fecha' in query_string:
            fecha = request.args.get('fecha')

            fecha_filter = datetime.strptime(str(fecha), "%Y-%m-%d")

            data['fechaRecepcion'] = fecha_filter

            filter_spec.append({'field': 'fechaRecepcion', 'op': '==', 'value': fecha_filter})

        if 'estatus' in query_string:
            status_inversion = request.args.get('estatus')

            data['estatus'] = status_inversion

            filter_spec.append({'field': 'estatus', 'op': 'ilike', 'value': status_inversion})

        gin_inv_model = GinInversionesModel(data)

        inversiones_on_db = gin_inv_model.get_properties_by_filters(session_db, filter_spec)

        if not bool(inversiones_on_db) or not inversiones_on_db or "[]" == inversiones_on_db:
            return HandlerResponse.resp_success(ErrorMsg.ERROR_DATA_NOT_FOUND, {})

        return HandlerResponse.resp_success(SuccessMsg.MSG_GET_RECORD, inversiones_on_db)

    # elif request.method == 'PUT':
    #
    #     data = request.get_json(force=True)
    #
    #     gin_inv_model = GinInversionesModel(data)
    #
    #     if not data:
    #         return HandlerResponse.request_conflict()
    #
    #     json_data = dict()
    #
    #     json_data = gin_inv_model.update_data(session_db, data)
    #
    #     logger.info('Bank updated Info: %s', str(json_data))
    #
    #     if not json_data:
    #         return HandlerResponse.not_found()
    #
    #     return HandlerResponse.resp_success(json_data)
    #
    elif request.method == 'DELETE':

        data = dict()
        # data = request.get_json(force=True)

        filter_spec = []

        if not ('cuenta' in query_string) and ('canal' in query_string) and ('autorizacion' in query_string):
            return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)
        else:

            cuenta = request.args.get('cuenta')

            data['cuenta'] = cuenta

            canal = request.args.get('canal')

            data['canal'] = canal

            autorizacion = request.args.get('autorizacion')

            data['autorizacion'] = autorizacion

        gin_inv_model = GinInversionesModel(data)

        json_data = []

        if not data:
            return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

        json_response = gin_inv_model.delete_data(session_db, data)

        logger.info('Inversion deleted: %s', json_response)

        if not json_response:
            return HandlerResponse.resp_success(ErrorMsg.ERROR_DATA_NOT_FOUND, {})

        return HandlerResponse.resp_success(SuccessMsg.MSG_DELETED_RECORD, json_response)

    else:
        return HandlerResponse.not_found(ErrorMsg.ERROR_REQUEST_NOT_FOUND)


@inversiones_api.route('/flujo/datos', methods=['POST'])
def endpoint_flujo_datos():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    # auth = headers.get('Authorization')

    # if not auth and 'Bearer' not in auth:
    #     return HandlerResponse.request_unauthorized()
    # else:

    if request.method == 'POST':
        # GUARDAR DATOS DE INVERSIONES

        data = request.get_json(force=True)

        gin_inv_model = GinInversionesModel(data)

        if not data or str(data) is None:
            return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT)

        logger.info('Data Json Inversion to Manage on DB: %s', str(data))

        json_inversion_added = gin_inv_model.save_inversion(session_db, data)

        if not json_inversion_added:
            return HandlerResponse.resp_success(SuccessMsg.MSG_RECORD_REGISTERED, {})

        return HandlerResponse.resp_success(SuccessMsg.MSG_CREATED_RECORD, json_inversion_added)


@authorization_api.route('/', methods=['POST'])
def get_authentication():

    json_token = {}

    if request.method == 'POST':
        data = request.get_json(force=True)

        user_name = data['username']
        password = data['password']
        # rfc = data['rfc_client']

        regex_email = r"^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$"

        regex_passwd = r"^[(A-Za-z0-9\_\-\.\$\#\&\*)(A-Za-z0-9\_\-\.\$\#\&\*)]+"

        # regex_rfc = r
        # "^([A-ZÑ&]{3,4})?(?:-?)?(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01]))?(?:-?)?([A-Z\d]{2})([A\d])$"

        match_email = re.match(regex_email, user_name, re.M | re.I)

        match_passwd = re.match(regex_passwd, password, re.M | re.I)

        # match_rfc = re.match(regex_rfc, rfc, re.M | re.I)

        if match_email and match_passwd:

            password = password + '_' + cfg_app.api_key

            json_token = json.dumps(user_registration(user_name, password))

            # json_token = json.dumps(json_token)

            return json_token

        else:
            return HandlerResponse.request_conflict()
    else:
        return HandlerResponse.request_not_found()
