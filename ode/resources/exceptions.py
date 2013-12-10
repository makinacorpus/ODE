import json

from webob import Response, exc


class JsonException(exc.HTTPError):

    def __init__(self, status_code, message):
        body = {
            'status': status_code,
            'errors': [
                {'description': message or self.message}
            ]
        }
        Response.__init__(self, json.dumps(body))
        self.status = status_code
        self.content_type = 'application/vnd.collection+json'


class HTTPNotFound(JsonException):

    def __init__(self, message='Not found'):
        JsonException.__init__(self, 404, message)


class HTTPBadRequest(JsonException):

    def __init__(self, message='Bad request'):
        JsonException.__init__(self, 400, message)
