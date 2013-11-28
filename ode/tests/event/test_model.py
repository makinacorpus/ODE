# -*- encoding: utf-8 -*-
from unittest import TestCase
from datetime import datetime

from ode.models import DBSession
from ode.tests.event import TestEventMixin
from ode.models import flatten_values


class TestModel(TestEventMixin, TestCase):

    def test_start_time(self):
        start_time = datetime(2013, 01, 01)
        event = self.create_event(start_time=start_time)
        self.assertEqual(event.locations[0].dates[0].start_time, start_time)
        self.assertIsNone(event.locations[0].dates[0].start_time.tzinfo)

    def test_end_time(self):
        end_time = datetime(2013, 01, 01)
        event = self.create_event(end_time=end_time)
        self.assertEqual(event.locations[0].dates[0].end_time, end_time)
        self.assertIsNone(event.locations[0].dates[0].end_time.tzinfo)

    def test_uid(self):
        start_time = datetime(2013, 01, 01)
        event = self.create_event(start_time=start_time)
        DBSession.flush()
        self.assertTrue(event.uid.endswith("@example.com"))

    def test_flatten_values(self):
        input_struct = {
            'a': {'value': 1},
            'b': {'value': 2},
            'c': None,
            'd': 3,
        }
        self.assertEqual(
            flatten_values(input_struct),
            {'a': 1, 'b': 2, 'c': None, 'd': 3},
        )
