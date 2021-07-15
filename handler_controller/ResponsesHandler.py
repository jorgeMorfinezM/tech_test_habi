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
from flask import Flask, jsonify, request
from werkzeug import exceptions
# import api_config

app = Flask(__name__)


class ResponsesHandler(exceptions.HTTPException):

    # @app.errorhandler(200)
    @staticmethod
    def response_success(msg, data):

        if bool(data):
            data_msg = json.loads(data)
        else:
            data_msg = data

        message = {
            'message': msg,
            'data': data_msg
        }

        resp = jsonify(message)
        status_code = 200

        return resp, int(status_code)

    # @app.errorhandler(201)
    @staticmethod
    def response_resource_created(data, msg):

        if bool(data):
            data_msg = json.loads(data)
        else:
            data_msg = data

        message = {
            'message': msg,
            'data': data_msg
        }

        resp = jsonify(message)
        status_code = 201

        return resp, status_code

    # @app.errorhandler(400)
    @staticmethod
    def bad_request(msg):
        message = {
            'message': msg + request.url,
            'data': {}
        }

        resp = jsonify(message)
        status_code = 400

        return resp, status_code

    # @app.errorhandler(401)
    @staticmethod
    def request_unauthorized(msg, data_msg):
        message = {
            'message': msg + request.url,
            'data': data_msg
        }

        resp = jsonify(message)
        status_code = 401

        return resp, status_code

    # @app.errorhandler(404)
    @staticmethod
    def request_not_found(msg):
        message = {
            'message': msg + request.url,
            'data': {}
        }

        resp = jsonify(message)
        status_code = 404

        return resp, status_code

    # @app.errorhandler(405)
    @staticmethod
    def request_method_not_allowed(msg):
        message = {
            'message': msg + request.url,
            'data': {}
        }

        resp = jsonify(message)
        status_code = 405

        return resp, status_code

    # @app.errorhandler(409)
    @staticmethod
    def request_conflict(msg, data_msg):
        message = {
            'message': msg + request.url,
            'data': data_msg
        }

        resp = jsonify(message)
        status_code = 409

        return resp, status_code

    # @app.errorhandler(500)
    @staticmethod
    def internal_server_error(msg):
        message = {
            'message': msg + request.url,
            'data': {}
        }

        resp = jsonify(message)
        status_code = 500

        return resp, status_code

    # @app.errorhandler(503)
    @staticmethod
    def service_unavailable(msg):
        message = {
            'message': msg + request.url,
            'data': {}
        }

        resp = jsonify(message)
        status_code = 503

        return resp, status_code
