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
        self.assertIsNone(event.start_time.tzinfo)

    def test_end_time(self):
        end_time = datetime(2013, 01, 01)
        event = self.create_event(end_time=end_time)
        self.assertEqual(event.end_time, end_time)
        self.assertIsNone(event.end_time.tzinfo)

    def test_uid(self):
        start_time = datetime(2013, 01, 01)
        event = self.create_event(start_time=start_time)
        DBSession.flush()
        self.assertTrue(event.id.endswith("@example.com"))

    def test_tags(self):
        tags = ['tag1', 'tag2']
        event1 = self.create_event(tags=tags)
        DBSession.flush()
        self.assertTrue(event1.id.endswith("@example.com"))
        self.assertEqual(event1.tags[0].name, 'tag1')
        tag = event1.tags[0]
        event2 = self.create_event(tags=tags)
        DBSession.flush()
        self.assertTrue(event2.id.endswith("@example.com"))
        self.assertEqual(event2.tags[0].name, 'tag1')
        self.assertEqual(tag, event2.tags[0])

    def test_categories(self):
        categories = ['category1', 'category2']
        event1 = self.create_event(categories=categories)
        DBSession.flush()
        self.assertTrue(event1.id.endswith("@example.com"))
        self.assertEqual(event1.categories[0].name, 'category1')
        category = event1.categories[0]
        event2 = self.create_event(categories=categories)
        DBSession.flush()
        self.assertTrue(event2.id.endswith("@example.com"))
        self.assertEqual(event2.categories[0].name, 'category1')
        self.assertEqual(category, event2.categories[0])

    def test_same_tag_and_category(self):
        event = self.create_event(tags=['tag'], categories=['tag'])
        DBSession.flush()
        self.assertTrue(event.id.endswith("@example.com"))
        self.assertEqual(event.tags[0].name, 'tag')
        self.assertEqual(event.categories[0].name, 'tag')
