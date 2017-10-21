#!/usr/bin/env python
# coding=utf-8

import re
import six
import hmac
import time

from .request import Request, WebSocket
from hashlib import sha256

re_path_template = re.compile('{\w+}')

def underline_to_camel(underline_format):
    camel_format = ''
    if isinstance(underline_format, str):
        splits = underline_format.split('_')
        camel_format += splits[0]
        for _s_ in splits[1:]:
            camel_format += _s_.capitalize()
    return camel_format

class BinanceClientError(Exception):
    def __init__(self, error_message, status_code=None):
        self.status_code = status_code
        self.error_message = error_message

    def __str__(self):
        if self.status_code:
            return "(%s) %s" % (self.status_code, self.error_message)
        else:
            return self.error_message

class BinanceWebSocketClientError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message

    def __str__(self):
        return self.error_message

class BinanceAPIError(Exception):
    def __init__(self, status_code, error_code, error_message, *args, **kwargs):
        self.status_code = status_code
        self.error_code = error_code
        self.error_message = error_message

    def __str__(self):
        return "(%s) %s: %s" % (self.status_code, self.error_code, self.error_message)

def bind_method(**config):

    class BinanceAPIMethod(object):
        path = config['path']
        method = config.get('method', 'GET')
        accepts_parameters = [underline_to_camel(param) for param in config.get("accepts_parameters", [])]
        signature = config.get("signature", False)
        api_key_required = config.get("api_key_required", False)
        root_class = config.get('root_class', None)
        response_type = config.get("response_type", "list")
        
        def __init__(self, api, *args, **kwargs):
            self.api = api
            self.return_json = kwargs.pop("return_json", False)
            self.parameters = {}
            self._build_parameters(args, kwargs)

        def _build_parameters(self, args, kwargs):
            for index, value in enumerate(args):
                if value is None:
                    continue

                try:
                    self.parameters[self.accepts_parameters[index]] = str(value)
                except IndexError:
                    raise BinanceClientError("Too many arguments supplied") 

            for key, value in six.iteritems(kwargs):
                if value is None:
                    continue
                key = underline_to_camel(key)
                if key in self.parameters:
                    raise BinanceClientError("Parameter %s already supplied" % key)
                self.parameters[key] = str(value)

            if "timestamp" in self.accepts_parameters and "timestamp" not in self.parameters:
                self.parameters["timestamp"] = int(time.time() * 1000)

            if self.signature and self.api.api_key != None:
                signature_parameters_string = \
                    "&".join(["%s=%s" % (key, value) for key, value in self.parameters.items()])
                self.parameters["signature"] = hmac.new(self.api.secret_key.encode(), signature_parameters_string.encode(), sha256).hexdigest()

        def _do_api_request(self, url, method="GET", body=None, headers=None):
            headers = headers or {}
            if self.signature and self.api.api_key != None or self.api_key_required:
                headers["X-MBX-APIKEY"] = self.api.api_key

            response = Request(self.api).make_request(url, method=method, body=body, headers=headers)
            try:
                content_obj = response.json()
            except ValueError:
                raise BinanceClientError('Unable to parse response, not valid JSON.', status_code=response.status_code)

            if "code" in content_obj and "msg" in content_obj:
                raise BinanceAPIError(response.status_code, content_obj["code"], content_obj["msg"])

            api_responses = []

            if self.response_type == "list":
                for entry in content_obj:
                    if self.return_json:
                        api_responses.append(entry)
                    else:
                        obj = self.root_class.object_from_dictionary(entry)
                        api_responses.append(obj)
            elif self.response_type == "entry":
                if self.return_json:
                    api_responses = content_obj
                else:
                    api_responses = self.root_class.object_from_dictionary(content_obj)
            elif self.response_type == "empty":
                api_responses = {}

            return api_responses
                    
        def execute(self):
            url, method, body, headers = Request(self.api).prepare_request(self.method,
                                                                           self.path,
                                                                           self.parameters)
            content = self._do_api_request(url, method, body, headers)
            return content

    def _call(api, *args, **kwargs):
        method = BinanceAPIMethod(api, *args, **kwargs)
        return method.execute()

    return _call

def bind_ws_method(**config):
    
    class BinanceWebSocketAPIMethod(object):
        path = config['path']
        accepts_parameters = [underline_to_camel(param) for param in config.get("accepts_parameters", [])]
        root_class = config.get('root_class', None)
        response_type = config.get("response_type", "list")
        
        def __init__(self, api, *args, **kwargs):
            self.api = api
            self.callback = kwargs.pop("callback", None)
            self.return_json = kwargs.pop("return_json", False)
            self.parameters = {}
            self._build_parameters(args, kwargs)
            self._build_path()

        def _build_parameters(self, args, kwargs):
            for index, value in enumerate(args):
                if value is None:
                    continue

                try:
                    self.parameters[self.accepts_parameters[index]] = str(value)
                except IndexError:
                    raise BinanceWebSocketClientError("Too many arguments supplied") 

            for key, value in six.iteritems(kwargs):
                if value is None:
                    continue
                key = underline_to_camel(key)
                if key in self.parameters:
                    raise BinanceWebSocketClientError("Parameter %s already supplied" % key)
                self.parameters[key] = str(value)

        def _build_path(self):
            for variable in re_path_template.findall(self.path):
                name = underline_to_camel(variable.strip('{}'))
                try:
                    value = self.parameters[name].lower() if name == "symbol" else self.parameters[name] 
                except KeyError:
                    raise BinanceWebSocketClientError('No parameter value found for path variable: %s' % name)
                del self.parameters[name]
                
                self.path = self.path.replace(variable, value)

        def _callback(self, content_obj):
            api_responses = []
            if self.response_type == "list":
                for entry in content_obj:
                    if self.return_json:
                        api_responses.append(entry)
                    else:
                        obj = self.root_class.object_from_dictionary(entry)
                        api_responses.append(obj)
            elif self.response_type == "entry":
                if self.return_json:
                    api_responses = content_obj
                else:
                    api_responses = self.root_class.object_from_dictionary(content_obj)
            elif self.response_type == "empty":
                api_responses = {}

            self.callback(api_responses)
            
        def _run_subscribe(self, url):
            WebSocket(self.api, self._callback).run_forever(url)
                    
        def execute(self):
            url = WebSocket(self.api).prepare_request(self.path)
            self._run_subscribe(url)

    def _subscribe(api, *args, **kwargs):
        method = BinanceWebSocketAPIMethod(api, *args, **kwargs)
        return method.execute()

    return _subscribe
