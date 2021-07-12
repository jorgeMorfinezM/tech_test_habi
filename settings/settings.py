# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021"
__license__ = ""
__history__ = """ """
__version__ = "1.21.G04.5 ($Rev: 5 $)"

import os
import uuid
from os.path import join, dirname
from dotenv import load_dotenv


class Constants:
    def __init__(self):
        # Create .env_temp file path.
        dotenv_path = join(dirname(__file__), '.env')

        # Load file from the path.
        load_dotenv(dotenv_path)

    class Development(object):
        """
        Development environment configuration
        """
        DEBUG = True
        TESTING = True
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    class Production(object):
        """
        Production environment configurations
        """
        DEBUG = False
        TESTING = False
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class AppConstants(Constants):

    log_file_apply = bool()
    log_types = list()
    log_file_extension = str()
    log_file_app_name = str()
    log_file_save_path = str()
    flask_api_debug = str()
    flask_api_env = str()
    flask_api_port = int()
    app_config = {}
    date_timezone = str()
    api_key = str()

    def __init__(self):
        super().__init__()

        app_config = {
            'development': Constants.Development,
            'production': Constants.Production,
        }

        self.log_file_apply = os.getenv('APPLY_LOG_FILE')
        self.log_types = os.getenv('LOGGER_TYPES')
        self.log_file_extension = os.getenv('FILE_LOG_EXTENSION')
        self.log_file_app_name = os.getenv('APP_FILE_LOG_NAME')
        self.log_file_save_path = os.getenv('DIRECTORY_LOG_FILES')
        self.app_config = app_config
        self.flask_api_debug = os.getenv('FLASK_DEBUG')
        self.flask_api_env = os.getenv('FLASK_ENV')
        self.flask_api_port = os.getenv('FLASK_PORT')
        self.date_timezone = os.getenv('TIMEZONE')
        self.api_key = os.getenv('API_KEY')


class DbConstants(Constants):

    property_table = str()         # PROPERTY_TABLE
    status_property_table = str()  # STATUS_PROPERTY_TABLE
    user_table = str()             # USER_TABLE
    like_table = str()             # LIKE_TABLE
    status_history_table = str()   # STATUS_HISTORY_TABLE

    def __init__(self):
        super().__init__()

        self.property_table = os.getenv('PROPERTY_TABLE').__str__()
        self.status_property_table = os.getenv('STATUS_PROPERTY_TABLE').__str__()
        self.user_table = os.getenv('USER_TABLE').__str__()
        self.like_table = os.getenv('LIKE_TABLE').__str__()
        self.status_history_table = os.getenv('STATUS_HISTORY_TABLE').__str__()
