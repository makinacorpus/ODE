import json
import requests
from urlparse import urlparse
import logging

log = logging.getLogger(__name__)

from colander import Invalid

from ode.models import DBSession, Source, Event
from ode.validation.schema import EventSchema
from deserializers import icalendar_extractor, json_extractor


def exists(uid):
    return DBSession.query(Event).filter_by(id=uid).count() > 0


def validate(cstruct):
    schema = EventSchema()
    return schema.deserialize(cstruct)


class HarvestRequest(object):

    def __init__(self, body):
        self.body = body


def harvest_cstruct(cstruct, source):
    for item in cstruct['items']:
        if 'id' in item['data']:
            item['data']['id'] += '@' + urlparse(source.url).hostname
        if exists(item['data']['id']):
            event = Event.get_by_id(item['data']['id'])
            appstruct = validate(item['data'])
            event.update_from_appstruct(appstruct)
            DBSession.merge(event)
        else:
            try:
                model_kwargs = validate(item['data'])
            except Invalid:
                continue
            event = Event(**model_kwargs)
            DBSession.add(event)


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
