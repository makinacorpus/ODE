.. Open Data Events documentation master file, created by
   sphinx-quickstart on Thu Oct 17 17:34:37 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ODE API documentation
=====================

ODE allows clients to interact with two kinds of resources: events and sources.
Sources are simply URLs pointing to event streams in iCalendar format that get
fetched in the background to populate the ODE database.


The ODE API is based on
`Collection+JSON <http://amundsen.com/media-types/collection/>`_, a JSON-based
read/write hypermedia-type designed to support management and querying of simple collections.
Events can also be represented in `iCalendar <https://tools.ietf.org/html/rfc5545>`_ and CSV formats.
Note that we don't use the Collection+JSON format for error reports because it's not
flexible enough for our needs. Errors are reported in `Cornice format <https://cornice.readthedocs.org/en/latest/validation.html?highlight=error#dealing-with-errors>`_.

Assuming you've setup your web server to serve this API at the root of your
domain name, your endpoints will be:

* /v1/events
* /v1/sources

Collection+JSON and ODE follow typical RESTful conventions:

* POST to add a new items, eg. ``POST /v1/events`` to add a new event
* PUT to update and existing item, eg. ``PUT /v1/sources/123`` to modify the source with id ``123``
* GET to get a list of items or a specific item, eg. ``GET /v1/sources`` to get a list of sources or ``GET /v1/events/123`` to get a representation of the event with id ``123``.
* The ``Accept`` request header to specify which format you want to retrieve, eg. ``Accept: text/calendar`` to get events in iCalendar format.
* The ``Content-Type`` request header to specify which format you provide, eg. ``Content-Type: text/csv`` to inform the server that you're sending comma-separated values.


Collection requests accept query string parameters:

* ``limit``: maximum number of items
* ``offset``: index of the first item
* ``sort_by``: name of an attribute to sort the collection
* ``sort_direction``: either ``asc`` (ascending order) or ``desc`` (descending order). default to ``asc``.
* ``provider_id``: filter by provider id

For example, if you'd like to retrive events 20 to 30 sorted by start time in descending order, you'd use a URL such as::

    /v1/events?offset=20&limit=10&sort_by=start_time&sort_direction=desc

.. services::
   :modules: ode.resources.event, ode.resources.source

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

