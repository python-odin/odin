#########################
Mapping between resources
#########################


Defining a mapping
==================

::

    import odin

    class CalendarEvent(odin.Resource):
        name = odin.StringField()
        start_date = odin.DateTimeField()

    class CalendarEventFrom(odin.Resource):
        name = odin.StringField()
        event_date = odin.DateTimeField()
        event_hour = odin.IntegerField()
        event_minute = odin.IntegerField()

    class CalendarEventToEventFrom(odin.Mapping):
        from_resource = CalendarEventResource
        to_resource = CalendarEventFromResource

        mappings = (
            # (From Field, Transformation, To Field)
            ('start_date', None, 'event_date'),
        )

        @odin.map_field
        def name(self, v):
            return v.upper()

        @odin.map_field(to_field=('event_hour', 'event_minute'))
        def start_date(self, v):
            return v.hour, v.minute


Converting between resources
============================

::

    # Create and instance of a CalendarEvent
    >>> event = CalendarEventResource(
        name='Launch Party',
        start_date=datetime.datetime(2014, 01, 11, 22, 30)
        )

    # Convert to CalendarEventFrom
    >>> event_from = event.convert_to(CalendarEventFrom)

