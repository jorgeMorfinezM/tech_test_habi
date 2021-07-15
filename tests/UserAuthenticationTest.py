# -*- coding: utf-8 -*-
"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021, Jorge Morfinez Mojica"
__license__ = ""
__history__ = """ """
__version__ = "1.1.A25.1 ($Rev: 1 $)"

import json
from tests.BaseCase import BaseCase


class TestUserLogin(BaseCase):

    def test_successful_login(self):

        user_name = "jorge.morfinez.m@gmail.com"
        password = "Jm$_&1388"
        email = "jorge.morfinez.m@gmail.com"

        payload = json.dumps({
            "username": user_name,
            "password": password,
            "email": email,
            "first_name": "Jorge",
            "last_name": "Morfinez",
            "is_active": 1,
            "is_staff": 0,
            "is_superuser": 0,
        })

        # When
        response = self.app.post('/api/v1/manager/user/register/', headers={"Content-Type": "application/json"},
                                 data=payload)

        token_response = json.loads(response.get_data(as_text=True))

        # Then
        self.assertEqual(str, type(token_response['message']))
        self.assertEqual(str, type(token_response['access_token']))
        self.assertEqual(str, type(token_response['refresh_token']))
        self.assertEqual(200, response.status_code)

    def test_login_already_existing_user(self):
        user_name = "jorge.morfinez.m@gmail.com"
        password = "Jm$_&1388_$23546"
        email = "jorge.morfinez.m@gmail.com"

        payload = json.dumps({
            "username": user_name,
            "password": password,
            "email": email,
            "first_name": "Jorge A.",
            "last_name": "Morfinez Mojica",
            "is_active": 1,
            "is_staff": 1,
            "is_superuser": 0,
        })

        # When
        response = self.app.put('/api/v1/manager/user/', headers={"Content-Type": "application/json"}, data=payload)

        user_response = json.loads(response.get_data(as_text=True))

        # Then
        self.assertEqual(str, type(user_response['Username']))
        self.assertEqual(str, type(user_response['Password']))
        self.assertEqual(str, type(user_response['Email']))
        self.assertEqual(str, type(user_response['FirstName']))
        self.assertEqual(str, type(user_response['LastName']))
        self.assertEqual(str, type(user_response['IsActive']))
        self.assertEqual(str, type(user_response['IsStaff']))
        self.assertEqual(str, type(user_response['IsSuperUser']))
        self.assertEqual(str, type(user_response['DateJoined']))
        self.assertEqual(200, response.status_code)

    def test_login_with_invalid_username(self):
        user_name = "jorgemorfinez_gmail.com"
        password = "Jm$_&1388"
        email = "jorgemorfinez_gmail_com"

        payload = json.dumps({
            "username": user_name,
            "password": password,
            "email": email,
            "first_name": "Jorge A.",
            "last_name": "Morfinez Mojica",
            "is_active": 1,
            "is_staff": 0,
            "is_superuser": 0,
        })

        # When
        response = self.app.post('/api/v1/manager/user/register/', headers={"Content-Type": "application/json"},
                                 data=payload)

        user_response = json.loads(response.get_data(as_text=True))

        # Then
        self.assertEqual(str, type(user_response['message']))
        self.assertEqual(str, type(user_response['data']))

    def test_login_with_invalid_password(self):
        user_name = "jorge_morfinez_m@gmail.com"
        password = "Ñ"
        email = "jorge.morfinez.m@gmail.com"

        payload = json.dumps({
            "username": user_name,
            "password": password,
            "email": email,
            "first_name": "Jorge A.",
            "last_name": "Morfinez Mojica",
            "is_active": 1,
            "is_staff": 0,
            "is_superuser": 0,
        })

        # When
        response = self.app.patch('/api/v1/manager/user/', headers={"Content-Type": "application/json"}, data=payload)

        user_response = json.loads(response.get_data(as_text=True))

        # Then
        self.assertEqual(str, type(user_response['message']))
        self.assertEqual(str, type(user_response['data']))

    def test_login_get_users(self):

        # When
        response = self.app.get('/api/v1/manager/user/', headers={"Content-Type": "application/json"})

        user_response = json.loads(response.get_data(as_text=True))

        # Then
        self.assertEqual(str, type(user_response["AuthUser"]['Username']))
        self.assertEqual(str, type(user_response["AuthUser"]['Password']))
        self.assertEqual(str, type(user_response["AuthUser"]['Email']))
        self.assertEqual(str, type(user_response["AuthUser"]['FirstName']))
        self.assertEqual(str, type(user_response["AuthUser"]['LastName']))
        self.assertEqual(str, type(user_response["AuthUser"]['IsActive']))
        self.assertEqual(str, type(user_response["AuthUser"]['IsStaff']))
        self.assertEqual(str, type(user_response["AuthUser"]['IsSuperUser']))
        self.assertEqual(str, type(user_response["AuthUser"]['DateJoined']))
        self.assertEqual(200, response.status_code)

    def test_login_with_non_existing_field(self):
        user_name = "jorge.morfinez.m@gmail.com"
        password = "Jm$_&0398"
        email = "jorge.morfinez.m@gmail.com"

        data = "aeiou12345"

        payload = json.dumps({
            "username": user_name,
            "password": password,
            "email": email,
            "first_name": "Jorge A.",
            "last_name": "Morfinez Mojica",
            "is_active": 1,
            "is_staff": 0,
            "is_superuser": 0,
            "data": data,
        })

        # When
        response = self.app.put('/api/v1/manager/user/', headers={"Content-Type": "application/json"}, data=payload)

        user_response = json.loads(response.get_data(as_text=True))

        # Then
        self.assertEqual(str, type(user_response['message']))
        self.assertEqual(str, type(user_response['data']))

