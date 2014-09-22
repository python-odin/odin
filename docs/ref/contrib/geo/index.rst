#################
Geographic Values
#################

Fields and data types that handle latitude and longitude values.

:todo: This section is in progress

Datatypes
*********

latitude
========

A latitude value. A latitude is a value between -90.0 and 90.0.


longitude
=========

A longitude value. A longitude is a value between -180.0 and 180.0.


latlng
======

Combination latitude and longitude value.


point
=====

A point in cartesian space. This type can be either 2D (on a plain) or 3D (includes a z-axis).


Fields
******

.. _field-latitude_field:

LatitudeField
=============

``class LatitudeField([min_value=None, max_value=None, **options])``

A latitude.

LatitudeField has two extra arguments:

:py:attr:`LatitudeField.min_value`
    The minimum latitude that can be accepted (within the range of a latitude).

:py:attr:`LatitudeField.max_value`
    The maximum latitude that can be accepted (within the range of a latitude).


.. _field-longitude_field:

LongitudeField
==============

``class LongitudeField([min_value=None, max_value=None, **options])``

A longitude.

LongitudeField has two extra arguments:

:py:attr:`LongitudeField.min_value`
    The minimum longitude that can be accepted (within the range of a longitude).

:py:attr:`LongitudeField.max_value`
    The maximum longitude that can be accepted (within the range of a longitude).


.. _field-latlng_field:

LatLngField
===========

``class LatLngField([**options])``

A latlng.


.. _field-point_field:

PointField
==========

``class PointField([**options])``

A point.
