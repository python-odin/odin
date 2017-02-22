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
        super(CaseLessStringList, self).__init__(str(i).upper() for i in iterable)

    def __contains__(self, item):
        return super(CaseLessStringList, self).__contains__(str(item).upper())

    def extend(self, iterable):
        return super(CaseLessStringList, self).extend(str(i).upper() for i in iterable)

    def append(self, p_object):
        return super(CaseLessStringList, self).append(str(p_object).upper())

    def insert(self, index, p_object):
        return super(CaseLessStringList, self).insert(index, str(p_object).upper())

    def index(self, value, *args, **kwargs):
        return super(CaseLessStringList, self).index(str(value).upper(), *args, **kwargs)

    def remove(self, value):
        return super(CaseLessStringList, self).remove(str(value).upper())
