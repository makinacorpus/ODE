import json
import requests
from urlparse import urlparse
import logging

log = logging.getLogger(__name__)

from colander import Invalid

from ode.models import DBSession, Source, Event
from ode.validation.schema import EventSchema
from deserializers import icalendar_extractor, json_extractor


class HarvestRequest(object):

    def __init__(self, body):
        self.body = body


class EventCstruct(object):

    def __init__(self, cstruct):
        self.cstruct = cstruct

    def exists_in_database(self):
        uid = self.cstruct['data']['id']
        return DBSession.query(Event).filter_by(id=uid).count() > 0

    def validate(self):
        schema = EventSchema()
        return schema.deserialize(self.cstruct['data'])

    def has_uid_without_domain_name(self):
        return (
            'id' in self.cstruct['data']
            and
            u"@" not in self.cstruct['data']['id']
        )

    def append_domain_name_to_uid(self, source):
        self.cstruct['data']['id'] += '@' + urlparse(source.url).hostname

    def update_database(self):
        event = Event.get_by_id(self.cstruct['data']['id'])
        appstruct = self.validate()
        event.update_from_appstruct(appstruct)
        DBSession.merge(event)

    def insert_into_database(self):
        model_kwargs = self.validate()
        event = Event(**model_kwargs)
        DBSession.add(event)


def harvest_cstruct(cstruct, source):
    for item_cstruct in cstruct['items']:
        event_cstruct = EventCstruct(item_cstruct)
        if event_cstruct.has_uid_without_domain_name():
            event_cstruct.append_domain_name_to_uid(source)
        if event_cstruct.exists_in_database():
            event_cstruct.update_database()
        else:
            try:
                event_cstruct.insert_into_database()
            except Invalid:
                continue


def harvest():
    query = DBSession.query(Source)
    for source in query:
        try:
            response = requests.get(source.url)
            if response.status_code != 200:
                continue
            content = response.text
            try:
                json.loads(content)
                is_json = True
            except ValueError:
                is_json = False
            request = HarvestRequest(content)
            if is_json:
                cstruct = json_extractor(request)
            else:
                cstruct = icalendar_extractor(request)
            harvest_cstruct(cstruct, source)
        except Exception:
            log.warning(
                u"Failed to harvest source {id} with URL {url}".format(
                    id=source.id,
                    url=source.url,
                ), exc_info=True)
    DBSession.flush()
