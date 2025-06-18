import math

__all__ = ("latitude", "longitude", "latlng", "point")


def to_dms(value: float, absolute: bool = False) -> tuple[float, float, float]:
    """
    Split a float value into DMS (degree, minute, second) parts

    :param value: Float value to split
    :param absolute: Obtain the absolute value
    :return: tuple containing DMS values

    """
    invert = not absolute and value < 0
    value = abs(value)
    degree = int(math.floor(value))
    value = (value - degree) * 60
    minute = int(math.floor(value))
    second = (value - minute) * 60
    return (-degree if invert else degree), minute, second


def to_dm(value: float, absolute: bool = False) -> tuple[float, float]:
    """
    Split a float value into DM (degree, minute) parts

    :param value: Float value to split
    :param absolute: Obtain the absolute value
    :return: tuple containing DM values

    """
    invert = not absolute and value < 0
    value = abs(value)
    degree = int(math.floor(value))
    minute = (value - degree) * 60
    return (-degree if invert else degree), minute


class latitude(float):  # NoQA
    """
    A latitude value. A latitude is a value between -90.0 and 90.0.
    """

    def __new__(cls, x):
        lat = float.__new__(cls, x)
        if lat > 90.0 or lat < -90.0:  # noqa: PLR2004
            raise ValueError(f"not in range -90.0 -> 90.0: '{x}'")
        return lat

    def __str__(self):
        result = "{:02d}°{:02d}'{:02f}\"".format(*to_dms(self, True))
        return result + ("S" if self < 0 else "N")


class longitude(float):  # NoQA
    """
    A longitude value. A longitude is a value between -180.0 and 180.0.
    """

    def __new__(cls, x):
        lng = float.__new__(cls, x)
        if lng > 180.0 or lng < -180.0:  # noqa: PLR2004
            raise ValueError(f"not in range -180.0 -> 180.0: '{x}'")
        return lng

    def __str__(self):
        result = "{:03d}°{:02d}'{:02f}\"".format(*to_dms(self, True))
        return result + ("W" if self < 0 else "E")


class latlng(tuple):  # noqa: N801 - This is for consistency
    """Combination latitude and longitude value."""

    def __new__(cls, *args):
        # Unpack a tuple, list or latlng instance.
        if len(args) == 1 and isinstance(args[0], tuple | list):
            args = args[0]
        try:
            lat, lng = args
        except ValueError:
            raise TypeError(f"latlng() takes 2 arguments ({len(args)} given)") from None
        return tuple.__new__(cls, (latitude(lat), longitude(lng)))

    @property
    def lat(self):
        return self[0]

    @property
    def lng(self):
        return self[1]

    def __repr__(self):
        return "latlng({!r}, {!r})".format(*self)

    def __str__(self):
        return "({}, {})".format(*self)


class point(tuple):  # noqa: N801 - This is for consistency
    """A point in cartesian space.

    This type can be either 2D (on a plain) or 3D (includes a z-axis).
    """

    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], tuple | list):
            args = args[0]
        if len(args) in (2, 3):
            return tuple.__new__(cls, (float(x) for x in args))
        else:
            raise TypeError(f"point() takes 2-3 arguments ({len(args)} given)")

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        try:
            return self[2]
        except IndexError:
            raise AttributeError("2D points do not include a z axis.") from None

    @property
    def is_3d(self):
        return len(self) == 3  # noqa: PLR2004

    def __repr__(self):
        return ("point({}, {}, {})" if self.is_3d else "point({}, {})").format(*self)

    def __str__(self):
        return ("({}, {}, {})" if self.is_3d else "({}, {})").format(*self)
