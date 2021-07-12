# -*- coding: utf-8 -*-
"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021, Jorge Morfinez Mojica"
__license__ = ""
__history__ = """ """
__version__ = "1.1.A19.1 ($Rev: 1 $)"

from apps.user.AuthUserModel import AuthUserModel
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from logger_controller.logger_control import *
from db_controller.database_backend import *
import uuid


cfg_app = get_config_settings_app()


def generate_hash(password):
    return sha256.hash(password)


def verify_hash(password, hash_passwd):
    return sha256.verify(password, hash_passwd)


def user_registration(user_name, user_password):

    password_hash = generate_hash(user_password)

    logger_type = 'ws'

    log = configure_logger(logger_type)

    try:

        if verify_hash(user_password, password_hash):

            access_token = create_access_token(identity=user_name)

            refresh_token = create_refresh_token(identity=user_name)

            id_user = uuid.uuid1()

            AuthUserModel.manage_user_authentication(id_user.int, user_name, user_password, password_hash)

            # UsersAuth.manage_user_authentication('', user_name, user_password, password_hash)

            log.info('User inserted/updated in database: %s',
                     ' User_Name: "{}", Password_Hash: "{}" '.format(user_name,
                                                                     password_hash))
            return {
                'message': 'Logged in as {}'.format(user_name),
                'access_token': access_token,
                'refresh_token': refresh_token
            }

        else:
            return {'message': 'Wrong credentials'}

    except SQLAlchemyError as error:
        raise mvc_exc.ConnectionError(
            '"{}@{}" Can\'t connect to database, verify data connection to "{}".\nOriginal Exception raised: {}'.format(
                user_name, 'users_api', 'users_api', error
            )
        )
