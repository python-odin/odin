"""
Odin Data-structures
~~~~~~~~~~~~~~~~~~~~

Custom data-structures used within odin.

"""


class CaseLessStringList(list):
    """
    List that assumes all elements are lists and performs case less comparisons on them.

    Like a standard list this structure makes a copy of the existing data, while converting all entries to upper case
    strings.

    .. note:: All items added to this list are converted to upper case

    """

    def __init__(self, iterable):
        super().__init__(str(i).upper() for i in iterable)

    def __contains__(self, item):
        return super().__contains__(str(item).upper())

    def extend(self, iterable):
        return super().extend(str(i).upper() for i in iterable)

    def append(self, p_object):
        return super().append(str(p_object).upper())

    def insert(self, index, p_object):
        return super().insert(index, str(p_object).upper())

    def index(self, value, *args, **kwargs):
        return super().index(str(value).upper(), *args, **kwargs)

    def remove(self, value):
        return super().remove(str(value).upper())
