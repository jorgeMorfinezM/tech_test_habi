# -*- coding: utf-8 -*-
"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021, Jorge Morfinez Mojica"
__license__ = ""
__history__ = """ """
__version__ = "1.1.A25.1 ($Rev: 1 $)"

import unittest
import json
from tests.BaseCase import BaseCase


class TestManageProperty(BaseCase):

    def search_properties_filters(self):

        payload = {}
        files = [
            ('archivo', ('file', open('test/filters_properties_test.json', 'rb'), 'application/octet-stream'))
        ]

        header_request = {
            "Content-Type": "application/json",
        }

        response_search = self.app.get('/api/v1/manager/property/filter',
                                       headers=header_request, data=payload, files=files)

        # When
        list_property_response = json.loads(response_search.get_data(as_text=True))

        print("Response endpoint: ", list_property_response)

        # Then
        self.assertEqual(200, response_search.status_code)
        self.assertEqual(str, type(list_property_response["Propiedad"]["Domicilio"]))
        self.assertEqual(str, type(list_property_response["Propiedad"]["DomicilioEstado"]))
        self.assertEqual(str, type(list_property_response["Propiedad"]["DomicilioCiudad"]))
        self.assertEqual(str, type(list_property_response["Propiedad"]["Precio"]))
        self.assertEqual(str, type(list_property_response["Propiedad"]["Descripcion"]))

    def test_properties_with_non_existing_file(self):
        payload = {}
        files = [
            ('archivo', ('file', open('test/test.json', 'rb'), 'application/octet-stream'))
        ]

        header_request = {
            "Content-Type": "application/json",
        }

        response_search = self.app.get('/api/v1/manager/property/filter',
                                       headers=header_request, data=payload, files=files)

        # When
        list_property_response = json.loads(response_search.get_data(as_text=True))

        print("Response endpoint: ", list_property_response)

        # Then
        self.assertEqual(str, type(list_property_response['message']))
        self.assertEqual(int, type(list_property_response['data']))

    def test_properties_with_no_file(self):
        payload = {}
        files = []

        header_request = {
            "Content-Type": "application/json",
        }

        response_search = self.app.get('/api/v1/manager/property/filter',
                                       headers=header_request, data=payload, files=files)

        # When
        list_property_response = json.loads(response_search.get_data(as_text=True))

        print("Response endpoint: ", list_property_response)

        # Then
        self.assertEqual(str, type(list_property_response['message']))
        self.assertEqual(int, type(list_property_response['data']))