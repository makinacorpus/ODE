# -*- encoding: utf-8 -*-
from unittest import TestCase

from ode.deserializers import (
    data_list_to_dict,
    icalendar_extractor,
    json_extractor,
    csv_extractor
    )

json_sample = (
    '{"template": {"data": [{"name": "id", "value": "4c81f072630e11e3953c5c260'
    'a0e691e@example.com"}, {"name": "description", "value": "Description"}, {'
    '"name": "performers", "value": "artiste1, artiste2, artiste3"}, {"name": '
    '"press_url", "value": "http://presse"}, {"name": "price_information", "va'
    'lue": "tarif"}, {"name": "target", "value": "public"}, {"name": "title", '
    '"value": "Test medias"}, {"name": "start_time", "value": "2013-12-12T00:0'
    '0:00"}, {"name": "end_time", "value": "2013-12-28T00:00:00"}, {"name": "p'
    'ublication_start", "value": "2013-12-12T00:00:00"}, {"name": "publication'
    '_end", "value": "2013-12-28T00:00:00"}, {"name": "press_contact_email", "'
    'value": "aaa@aaa.aa"}, {"name": "press_contact_name", "value": "nom press'
    'e"}, {"name": "press_contact_phone_number", "value": "telephone presse"},'
    '{"name": "ticket_contact_email", "value": "aaa@aaa.aa"}, {"name": "ticket'
    '_contact_name", "value": "nom billetterie"}, {"name": "ticket_contact_pho'
    'ne_number", "value": "telephone billetterie"}, {"name": "location_name", '
    '"value": "Nom du lieu"}, {"name": "location_address", "value": "Adresse d'
    'u lieu"}, {"name": "location_post_code", "value": "Code postal"}, {"name"'
    ': "location_capacity", "value": "capacite"}, {"name": "location_town", "v'
    'alue": "Ville"}, {"name": "location_country", "value": "Pays"}, {"name": '
    '"tags", "value": ["tag1", "tag2", "tag3"]}, {"name": "categories", "value'
    '": ["category1", "category2"]}, {"name": "images", "value": [{"url": "htt'
    'p://photo", "license": "CC BY"}, {"url": "http://photo2", "license": "CC '
    'BY"}]}, {"name": "videos", "value": [{"url": "http://video", "license": "'
    'CC BY"}]}, {"name": "sounds", "value": [{"url": "http://audio", "license"'
    ': "CC BY"}]}]}}'
    )


csv_sample = ('id,firstname,lastname,email,telephone,description,language,latl'
              'ong,organiser,performers,press_url,price_information,source,sou'
              'rce_id,target,title,url,provider_id,start_time,end_time,publica'
              'tion_start,publication_end,press_contact_email,press_contact_na'
              'me,press_contact_phone_number,ticket_contact_email,ticket_conta'
              'ct_name,ticket_contact_phone_number,location_id,location_name,l'
              'ocation_address,location_post_code,location_capacity,location_t'
              'own,location_country,tags,categories,images,sounds,videos\n'
              '4c81f072630e11e3953c5c260a0e691e@example.com,,,,,Description,,,'
              ',"artiste1, art'
              'iste2, artiste3",http://presse,tarif,,,public,Test medias,,,201'
              '3-12-12T00:00:00,2013-12-28T00:00:00,2013-12-12T00:00:00,2013-1'
              '2-28T00:00:00,aaa@aaa.aa,nom presse,telephone presse,aaa@aaa.aa'
              ',nom billetterie,telephone billetterie,,Nom du lieu,Adresse du '
              'lieu,Code postal,capacite,Ville,Pays,"tag1, tag2, tag3","catego'
              'ry1, category2","http://photo (CC BY), http://photo2 (CC BY)",h'
              'ttp://audio (CC BY),http://video (CC BY)'
              )


ics_sample = '''BEGIN:VCALENDAR
BEGIN:VEVENT
SUMMARY:Test medias
DTSTART;VALUE=DATE-TIME:20131212T000000
DTEND;VALUE=DATE-TIME:20131228T000000
UID:4c81f072630e11e3953c5c260a0e691e@example.com
DESCRIPTION:Description
LOCATION:Nom du lieu
END:VEVENT
END:VCALENDAR'''


class TestExtractor(TestCase):

    cstruct_json = {
        'items': [
            {
                'data': {
                    'id': '4c81f072630e11e3953c5c260a0e691e@example.com',
                    'videos': [{'url': u'http://video', 'license': u'CC BY'}],
                    'images': [{'url': u'http://photo', 'license': u'CC BY'},
                               {'url': u'http://photo2', 'license': u'CC BY'}],
                    'ticket_contact_name': u'nom billetterie',
                    'location_post_code': u'Code postal',
                    'location_name': u'Nom du lieu',
                    'location_capacity': u'capacite',
                    'location_country': u'Pays',
                    'title': u'Test medias',
                    'description': u'Description',
                    'tags': [u'tag1', u'tag2', u'tag3'],
                    'start_time': u'2013-12-12T00:00:00',
                    'publication_end': u'2013-12-28T00:00:00',
                    'ticket_contact_phone_number': u'telephone billetterie',
                    'ticket_contact_email': u'aaa@aaa.aa',
                    'press_contact_phone_number': u'telephone presse',
                    'categories': [u'category1', u'category2'],
                    'location_town': u'Ville',
                    'press_contact_email': u'aaa@aaa.aa',
                    'target': u'public',
                    'publication_start': u'2013-12-12T00:00:00',
                    'performers': u'artiste1, artiste2, artiste3',
                    'price_information': u'tarif',
                    'sounds': [{'url': u'http://audio', 'license': u'CC BY'}],
                    'end_time': u'2013-12-28T00:00:00',
                    'location_address': u'Adresse du lieu',
                    'press_url': u'http://presse',
                    'press_contact_name': u'nom presse'
                    }
                }
            ]
        }

    cstruct_csv = {
        'items': [
            {
                'data': {
                    'id': '4c81f072630e11e3953c5c260a0e691e@example.com',
                    'provider_id': u'',
                    'videos': [{'url': u'http://video', 'license': u'CC BY'}],
                    'telephone': u'',
                    'organiser': u'',
                    'latlong': u'',
                    'images': [{'url': u'http://photo', 'license': u'CC BY'},
                               {'url': u'http://photo2', 'license': u'CC BY'}],
                    'ticket_contact_name': u'nom billetterie',
                    'location_id': u'', 'source_id': u'',
                    'location_post_code': u'Code postal',
                    'location_name': u'Nom du lieu',
                    'location_capacity': u'capacite',
                    'location_country': u'Pays',
                    'title': u'Test medias',
                    'source': u'',
                    'email': u'',
                    'description': u'Description',
                    'firstname': u'',
                    'tags': [u'tag1', u'tag2', u'tag3'],
                    'lastname': u'',
                    'start_time': u'2013-12-12T00:00:00',
                    'publication_end': u'2013-12-28T00:00:00',
                    'ticket_contact_phone_number': u'telephone billetterie',
                    'language': u'',
                    'ticket_contact_email': u'aaa@aaa.aa',
                    'press_contact_phone_number': u'telephone presse',
                    'categories': [u'category1', u'category2'],
                    'location_town': u'Ville',
                    'press_contact_email': u'aaa@aaa.aa',
                    'target': u'public',
                    'publication_start': u'2013-12-12T00:00:00',
                    'performers': u'artiste1, artiste2, artiste3',
                    'url': u'',
                    'price_information': u'tarif',
                    'sounds': [{'url': u'http://audio', 'license': u'CC BY'}],
                    'end_time': u'2013-12-28T00:00:00',
                    'location_address': u'Adresse du lieu',
                    'press_url': u'http://presse',
                    'press_contact_name': u'nom presse'
                    }
                }
            ]
        }

    cstruct_ics = {
        'items': [
            {
                'data': {
                    'id': '4c81f072630e11e3953c5c260a0e691e@example.com',
                    'location_name': u'Nom du lieu',
                    'title': u'Test medias',
                    'description': u'Description',
                    'start_time': u'2013-12-12T00:00:00',
                    'end_time': u'2013-12-28T00:00:00',
                    }
                }
            ]
        }

    class DummyRequest(object):

        def __init__(self, text):
            self.text = text

    def test_ics(self):
        request = self.DummyRequest(ics_sample)
        cstruct = icalendar_extractor(request)
        self.assertDictEqual(cstruct, self.cstruct_ics)

    def test_json(self):
        request = self.DummyRequest(json_sample)
        cstruct = json_extractor(request)
        self.assertDictEqual(cstruct, self.cstruct_json)

    def test_csv(self):
        request = self.DummyRequest(csv_sample)
        cstruct = csv_extractor(request)
        self.assertDictEqual(cstruct, self.cstruct_csv)


class TestDataListToDict(TestCase):

    def test_unique_values(self):
        data_list = [
            {u'name': u'title',
             u'value': u'Titre \xc9v\xe9nement'}
        ]
        expected_dict = {u'title': u'Titre \xc9v\xe9nement'}
        self.assertEqual(data_list_to_dict(data_list), expected_dict)

    def test_multiple_values(self):
        data_list = [
            {u'name': u'categories', u'value': u'Music'},
            {u'name': u'categories', u'value': u'Theatre'},
            {u'name': u'categories', u'value': u'Cinema'}
        ]
        expected_dict = {
            u'categories': [u'Music', u'Theatre', u'Cinema']
        }
        self.assertEqual(data_list_to_dict(data_list), expected_dict)
