#########################
Mapping between resources
#########################

Defining a mapping
==================

Given the following resources::

    import odin

    class CalendarEvent(odin.Resource):
        name = odin.StringField()
        start_date = odin.DateTimeField()

    class CalendarEventFrom(odin.Resource):
        name = odin.StringField()
        event_date = odin.DateTimeField()
        event_hour = odin.IntegerField()
        event_minute = odin.IntegerField()


A mapping can be defined to map from a basic ``Event`` to the ``EventFrom``::

    class CalendarEventToEventFrom(odin.Mapping):
        from_resource = CalendarEvent
        to_resource = CalendarEventFrom

        # Simple mappings (From Field, Transformation, To Field)
        mappings = (
            odin.define(from_field='start_date', to_field='event_date'),
        )

        # Mapping to multiple fields
        @odin.map_field(to_field=('event_hour', 'event_minute'))
        def start_date(self, v):
            # Return a tuple that is mapped to fields defined as to_fields
            return v.hour, v.minute


When a field name is matched on both resources it will be automatically mapped, for other fields mappings need to be
specified along with a transformation method or alternatively a method with a :py:meth:`map_field` decorator can be used
to handle more complex mappings.

.. hint::
    Both simple mappings and :py:meth:`map_field` can accept multiple fields as input and output, although care must be
    taken to ensure that the transformation method accepts and returns the same number of parameters as is defined in
    the mapping.


Converting between resources
============================

Once a mapping has been defined the :py:meth:`Resource.convert_to` or :py:meth:`Mapping.apply` are used to convert
between object, in addition :py:meth:`Mapping.update` can be used to update a existing object::

    # Create and instance of a CalendarEvent
    >>> event = CalendarEvent(
        name='Launch Party',
        start_date=datetime.datetime(2014, 01, 11, 22, 30))

    # Convert to CalendarEventFrom
    >>> event_from = event.convert_to(CalendarEventFrom)
    >>> event_from
    <CalendarEventFrom: example.resources.CalendarEventFrom resource>

    >>> event.to_dict()
    {'event_date': datetime.datetime(2014, 01, 11, 22, 30),
     'event_hour': 22,
     'event_minute': 30,
     'name': 'Launch Party'}

    # Or use the mapping definition CalendarEventToEventFrom
    >>> event_from = CalendarEventToEventFrom.apply(event)

    # Or update an an existing resource
    event.name = 'Grand Launch Party'
    event.update_existing(event_from)

    >>> event.to_dict()
    {'event_date': datetime.datetime(2014, 01, 11, 22, 30),
     'event_hour': 22,
     'event_minute': 30,
     'name': 'Grand Launch Party'}

    # Similarly the mapping definition can also be used
    >>> CalendarEventToEventFrom(event).update(event_from)
