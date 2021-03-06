# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021"
__license__ = ""
__history__ = """ """
__version__ = "1.21.G02.1 ($Rev: 2 $)"

import json
import logging
from datetime import datetime

import pymysql
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.reflection import Inspector
from db_controller import mvc_exceptions as mvc_exc
from logger_controller.logger_control import *
from utilities.Utility import *

from flask_bcrypt import Bcrypt

Base = declarative_base()
bcrypt = Bcrypt()

cfg_db = get_config_settings_db()
cfg_app = get_config_settings_app()

# logger = configure_logger(cfg_app.log_types[2].__str__())
logger = configure_logger('db')

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)


def create_engine_db():

    # For Test connection:

    engine = create_engine('mysql+pymysql://admin:HANrhz5u7e3jKqVQ@3.130.126.210:3309/habi_db',
                           execution_options={"isolation_level": "REPEATABLE READ"})

    if not 'development' == cfg_app.flask_api_env:
        engine = create_engine(cfg_db.Production.SQLALCHEMY_DATABASE_URI.__str__(),
                               execution_options={"isolation_level": "REPEATABLE READ"})

    logger.info("Engine Created by URL: {}".format(cfg_db.Development.SQLALCHEMY_DATABASE_URI.__str__()))

    print(f"URL DB: {cfg_db.Development.SQLALCHEMY_DATABASE_URI}")

    return engine


def create_database_api(engine_session):

    if not database_exists(engine_session.url):
        logger.info("Create the Database...")
        create_database(engine_session.url, 'utf-8')

    logger.info("Database created...")


def create_bd_objects(engine_obj):
    # inspector = Inspector.from_engine(engine_obj)
    #
    # table_names = list()
    #
    # table_names.append(cfg_db.gin_bancos_table.__str__())
    # table_names.append(cfg_db.gin_credenciales_table.__str__())
    # table_names.append(cfg_db.gin_inversiones_table.__str__())
    #
    # if not inspector.get_table_names():
    #     Base.metadata.create_all(bind=engine_obj)
    #     logger.info("Database objects created...")
    # else:
    #
    #     for table_name in inspector.get_table_names():
    #
    #         logger.info('Table on database: %s', str(table_name))
    #
    #         if table_name in table_names:
    #
    #             logger.info('Table already created: %s', str(table_name))
    #         else:
    #             # Create tables
    #             Base.metadata.create_all(bind=engine_obj)
    #
    #             logger.info("Database objects created...")

    Base.metadata.create_all(bind=engine_obj)

    logger.info("Database objects created...")


def session_to_db(engine_se):
    r"""
    Get and manage the session connect to the database engine.

    :return connection: Object to connect to the database and transact on it.
    """

    session = None

    connection = None

    try:

        if engine_se:

            session_maker = sessionmaker(bind=engine_se, autocommit=True)

            connection = engine_se.connect()

            session = session_maker(bind=connection)

            logger.info("Connection and Session objects created...")

        else:
            logger.error("Database not created or some parameters with the connection to the database can't be read")

    except mvc_exc.DatabaseError as db_error:
        logger.exception("Can not connect to database, verify data connection", db_error, exc_info=True)
        raise mvc_exc.ConnectionError(
            'Can not connect to database, verify data connection.\nOriginal Exception raised: {}'.format(db_error)
        )

    return connection, session


def init_db_connection():
    engine_db = create_engine_db()

    create_database_api(engine_db)

    create_bd_objects(engine_db)

    connection, session = session_to_db(engine_db)

    return connection, session


def scrub(input_string):
    """Clean an input string (to prevent SQL injection).

    Parameters
    ----------
    input_string : str

    Returns
    -------
    str
    """
    return "".join(k for k in input_string if k.isalnum())


def create_cursor(conn):
    r"""
    Create an object statement to transact to the database and manage his data.

    :param conn: Object to connect to the database.
    :return cursor: Object statement to transact to the database with the connection.

    """
    try:
        cursor = conn.cursor()

    except mvc_exc.ConnectionError as conn_error:
        logger.exception("Can not create the cursor object, verify database connection", conn_error, exc_info=True)
        raise mvc_exc.ConnectionError(
            'Can not connect to database, verify data connection.\nOriginal Exception raised: {}'.format(
                conn_error
            )
        )

    return cursor


def disconnect_from_db(conn):
    r"""
    Generate close session to the database through the disconnection of the conn object.

    :param conn: Object connector to close session.
    """

    if conn is not None:
        conn.close()


def close_cursor(cursor):
    r"""
    Generate close statement to the database through the disconnection of the cursor object.

    :param cursor: Object cursor to close statement.
    """

    if cursor is not None:
        cursor.close()


def get_current_date(session):
    sql_current_date = 'SELECT CURDATE()'  # For MySQL
    # sql_current_date = 'SELECT NOW()'  # For PostgreSQL

    current_date = session.execute(sql_current_date).one()

    logger.info('CurrentDate: %s', current_date)

    return current_date


def get_current_date_from_db(session, conn, cursor):
    r"""
    Get the current date and hour from the database server to set to the row registered or updated.

    :return last_updated_date: The current day with hour to set the date value.
    """

    last_updated_date = None

    try:

        sql_current_date = 'SELECT CURDATE()'  # For MySQL
        # sql_current_date = 'SELECT NOW()'  # For PostgreSQL

        cursor.execute(sql_current_date)

        result = cursor.fetchone()[0]

        # print("NOW() :", result)

        if result is not None:
            # last_updated_date = datetime.datetime.strptime(str(result), "%Y-%m-%d %H:%M:%S")
            # last_updated_date = datetime.datetime.strptime(str(result), "%Y-%m-%d %I:%M:%S")
            last_updated_date = result

        cursor.close()

    except SQLAlchemyError as error:
        conn.rollback()
        logger.exception('An exception occurred while execute transaction: %s', error)
        raise SQLAlchemyError(
            "A SQL Exception {} occurred while transacting with the database.".format(error)
        )
    finally:
        disconnect_from_db(conn)

    return last_updated_date
