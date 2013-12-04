# -*- encoding: utf-8 -*-
from unittest import TestCase

from ode.deserializers import data_list_to_dict


class TestDataListToDict(TestCase):

    def test_unique_values(self):
        data_list = [
            {u'name': u'title',
             u'value': u'Titre \xc9v\xe9nement'}
        ]
        expected_dict = {
            u'title': {'value': u'Titre \xc9v\xe9nement'},
        }
        self.assertEqual(data_list_to_dict(data_list), expected_dict)

    def test_multiple_values(self):
        data_list = [
            {u'name': u'category', u'value': u'Music'},
            {u'name': u'category', u'value': u'Theatre'},
            {u'name': u'category', u'value': u'Cinema'}
        ]
        expected_dict = {
            u'category': {
                'value': [
                    {'value': u'Music'},
                    {'value': u'Theatre'},
                    {'value': u'Cinema'},
                ]
            }
        }
        self.assertEqual(data_list_to_dict(data_list), expected_dict)
