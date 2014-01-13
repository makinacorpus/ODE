# -*- encoding: utf-8 -*-
from unittest import TestCase

from pyramid.httpexceptions import HTTPUnsupportedMediaType

from ode.tests.event import TestEventMixin


class TestContentType(TestEventMixin, TestCase):

    def test_post_unsupported_content_type(self):
        response = self.app.post('/v1/events',
                                 headers={
                                     'Content-Type': 'foo/bar',
                                     'X-ODE-Provider-Id': '123',
                                 },
                                 status=HTTPUnsupportedMediaType.code)
        self.assertErrorMessage(response, 'Content-Type header should be')

    def test_put_unsupported_content_type(self):
        event_id = self.post_event()
        response = self.app.put('/v1/events/%s' % event_id,
                                headers={
                                    'Content-Type': 'foo/bar',
                                    'X-ODE-Provider-Id': '123',
                                },
                                status=HTTPUnsupportedMediaType.code)
        self.assertErrorMessage(response, 'Content-Type header should be')
