# -*- encoding: utf-8 -*-
from unittest import TestCase

from ode.deserializers import collection_json_to_cstruct


class TestDeserializers(TestCase):

    def test_collection_json_simple_value(self):
        input_data = {
            u'collection': {
                u'items': [
                    {
                        u'data': [
                            {u'name': u'title',
                             u'value': u'Titre \xc9v\xe9nement'}
                        ]
                    }
                ]
            }
        }
        expected = {
            u'collection': {
                u'items': [
                    {
                        u'data': {
                            u'title': {'value': u'Titre \xc9v\xe9nement'},
                        }
                    }
                ]
            }
        }
        self.assertEqual(collection_json_to_cstruct(input_data),
                         expected)

    def test_collection_json_multiple_values(self):
        input_data = {
            u'collection': {
                u'items': [
                    {
                        u'data': [
                            {u'name': u'category', u'value': u'Music'},
                            {u'name': u'category', u'value': u'Theatre'},
                            {u'name': u'category', u'value': u'Cinema'}
                        ]
                    }
                ]
            }
        }
        expected = {
            u'collection': {
                u'items': [
                    {
                        u'data': {
                            u'category': {
                                'value': [
                                    {'value': u'Music'},
                                    {'value': u'Theatre'},
                                    {'value': u'Cinema'},
                                ]
                            }
                        }
                    }
                ]
            }
        }
        self.assertEqual(collection_json_to_cstruct(input_data),
                         expected)
