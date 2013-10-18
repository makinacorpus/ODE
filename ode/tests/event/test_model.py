# -*- encoding: utf-8 -*-
from unittest import TestCase
from datetime import datetime

from ode.models import DBSession
from ode.tests.event import TestEventMixin


class TestModel(TestEventMixin, TestCase):

    def test_start_time(self):
        start_time = datetime(2013, 01, 01)
        event = self.create_event(start_time=start_time)
        self.assertEqual(event.start_time, start_time)

    def test_end_time(self):
        end_time = datetime(2013, 01, 01)
        event = self.create_event(end_time=end_time)
        self.assertEqual(event.end_time, end_time)

    def test_uid(self):
        start_time = datetime(2013, 01, 01)
        event = self.create_event(start_time=start_time)
        DBSession.flush()
        self.assertEqual(event.uid,
                         "20130101000000-%s@example.com" % event.id)
