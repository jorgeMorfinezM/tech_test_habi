# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021"
__license__ = ""
__history__ = """ """
__version__ = "1.21.G02.1 ($Rev: 2 $)"

import threading
import time
from flask import Flask
from flask_jwt_extended import JWTManager
from apps.user.view_endpoints import user_auth_api
from apps.status_history.view_endpoints import status_history_api
from apps.status.view_endpoints import status_api
from apps.property.view_endpoints import property_api
# from db_controller.database_backend import *
from utilities.Utility import *

cfg_db = get_config_settings_db()
cfg_app = get_config_settings_app()


def create_app():
    app_api = Flask(__name__, static_url_path='/static')

    app_api.config['JWT_SECRET_KEY'] = '4p1/t3ch_t3st_#m4n4g3r%$_h4b1=2021-07-07/'
    app_api.config['JWT_BLACKLIST_ENABLED'] = False
    app_api.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    app_api.config['JWT_ERROR_MESSAGE_KEY'] = 'message'
    app_api.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
    app_api.config['PROPAGATE_EXCEPTIONS'] = True

    if not 'development' == cfg_app.flask_api_env:
        app_api.config['SQLALCHEMY_DATABASE_URI'] = cfg_db.Production.SQLALCHEMY_DATABASE_URI.__str__()

    app_api.config['SQLALCHEMY_DATABASE_URI'] = cfg_db.Development.SQLALCHEMY_DATABASE_URI

    # USERS_AUTH URL
    app_api.register_blueprint(user_auth_api, url_prefix='/api/v1/manager/user/')
    # app_api.register_blueprint(user_auth_api, url_prefix='/api/v1/manager/user/register/')

    # HISTORY STATUS URL
    app_api.register_blueprint(status_history_api, url_prefix='/api/v1/manager/status/history/')

    # STATUS URL
    app_api.register_blueprint(status_api, url_prefix='/api/v1/manager/status/')

    # PROPERTY URL
    app_api.register_blueprint(property_api, url_prefix='/api/v1/manager/property/')
    # app_api.register_blueprint(property_api, url_prefix='/api/v1/manager/property/filter')

    jwt = JWTManager(app_api)

    jwt.init_app(app_api)

    return app_api, jwt
