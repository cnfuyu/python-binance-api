#!/usr/bin/env python
# coding=utf-8

import logging
import requests
import websocket
import simplejson
import ssl
import six
from six.moves.urllib.parse import urlencode

from events import Events

logging.basicConfig()

class Request(object):
    def __init__(self, api):
        self.api = api

    def _is_wapi(self, path):
        return path.endswith('.html')

    def _get_base_path(self, path):
        return self.api.wapi_base_path if self._is_wapi(path) else self.api.base_path

    def _full_url(self, path):
        return "%s://%s%s%s" % (self.api.protocol,
                                self.api.host,
                                self._get_base_path(path),
                                path)
                                
    def _full_url_with_params(self, path, params):
        return (self._full_url(path) +
                self._full_query_with_params(params))

    def _full_query_with_params(self, params):
        signature = params.pop("signature", None)
        params = ("?" + urlencode(params)) if params else ""
        if signature is not None:
            params = params + "&signature=" + signature
        return params

    def _post_body(self, params):
        signature = params.pop("signature", None)
        body = list(params.items())
        if signature is not None:
            body = body + [("signature", signature)]
        return body

    def prepare_request(self, method, path, params):
        url = body = None
        headers = {}

        if method == "GET" or self._is_wapi(path):
            url = self._full_url_with_params(path, params)
        else:
            url = self._full_url(path) 
            body = self._post_body(params)

        return url, method, body, headers

    def make_request(self, url, method="GET", body=None, headers=None):
        headers = headers or {}
        if not 'User-Agent' in headers:
            headers.update({"User-Agent": "%s Python Client" % self.api.api_name})
        if method == "GET":
            return requests.get(url, headers=headers)
        elif method == "POST":
            return requests.post(url, data=body, headers=headers)
        elif method == "DELETE":
            return requests.delete(url, data=body, headers=headers)
        elif method == "PUT":
            return requests.put(url, data=body, headers=headers)

class WebSocket(Events):
    __events__ = ['callback']

    def __init__(self, api, callback=None):
        self.api = api
        self.callback += callback

    def _full_url(self, path):
        return "%s://%s:%s%s%s" % (self.api.protocol,
                                self.api.host,
                                self.api.port,
                                self.api.base_path,
                                path)

    def _on_message(self, ws, message):
        data = simplejson.loads(message)
        self.callback(data)

    def _on_error(self, ws, error):
        raise Exception(error)

    def prepare_request(self, path):
        url = self._full_url(path)

        return url

    def run_forever(self, url):
        self.ws = websocket.WebSocketApp(url,
                                         on_message=self._on_message,
                                         on_error=self._on_error)
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
