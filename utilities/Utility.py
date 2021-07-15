# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021"
__license__ = ""
__history__ = """ """
__version__ = "1.21.G02.1 ($Rev: 2 $)"

from settings.settings import *
from datetime import datetime
import base64
import pytz
import json


# Define y obtiene el configurador para las constantes generales del sistema
def get_config_settings_app():
    """
    Get the config object to charge the settings configurator.

    :return object: cfg object, contain the Match to the settings allowed in Constants file configuration.
    """

    settings_api = AppConstants()

    return settings_api


# Define y obtiene el configurador para las constantes de la base de datos
def get_config_settings_db():
    """
    Get the config object to charge the settings database configurator.

    :return object: cfg object, contain the Match to the settings allowed in Constants file configuration.
    """

    settings_db = DbConstants()

    return settings_db


# Cambia fecha-hora en datos a timezone UTC desde el dato y timezone definido
def set_utc_date_data(data_date, timezone_date):
    utc_date_convert = ""
    utc_hour_convert = ""

    date_on_utc = ""

    local_date = pytz.timezone(timezone_date)

    naive = datetime.strptime(data_date, "%Y-%m-%d %H:%M:%S")

    local_dt = local_date.localize(naive, is_dst=None)

    utc_dt = local_dt.astimezone(pytz.utc)

    print(utc_dt)

    date_on_utc = str(utc_dt).split()

    utc_date_convert = date_on_utc[0]
    utc_hour_convert = date_on_utc[1]

    return utc_date_convert, utc_hour_convert


# Obtiene los datos de los filtros a aplicar en Busqueda de Propiedades
def get_filter_property_file(filter_file):

    # print(filter_file.filename)

    with open(filter_file, "rb") as json_file:

        my_new_string_value = json_file.name

        # print(my_new_string_value)

        # xml_to_bytes = bytes(my_new_string_value, 'utf-8')

        xml_decoded = my_new_string_value.decode('utf-8')

        xml_decoded = xml_decoded.replace("b'", "")
        xml_decoded = xml_decoded.replace("'", "")

        json_object = json.loads(json.dumps(xml_decoded))

        json_file.close()

    return json_object


# Crea el query string para aplicar filtros a Propiedades
def make_query_string_filters(json_object):

    filters_query_string = "?"

    status_property = None
    build_year = None
    city_address = None
    province_address = None

    json_object = json.loads(json_object)

    if 'estatus' in json_object:
        # status_property = json_object['estatus']
        # status_property = '{}'.format(json_object['estatus'])
        status_property = json_object.get('estatus')

        filters_query_string += "estatus=" + status_property + "&"

    if 'anio_construccion' in json_object:
        build_year = json_object.get('anio_construccion')

        filters_query_string += "anio_construccion=" + str(build_year) + "&"

    if 'ciudad_propiedad' in json_object:
        city_address = json_object.get('ciudad_propiedad')

        filters_query_string += "ciudad_propiedad=" + city_address + "&"

    if 'estado_propiedad' in json_object:
        province_address = json_object.get('estado_propiedad')

        filters_query_string += "estado_propiedad=" + province_address + "&"

    return filters_query_string.rstrip('&')
