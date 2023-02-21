"""
Odin Data-structures
~~~~~~~~~~~~~~~~~~~~

Custom data-structures used within odin.

"""
from typing import Iterable, List


class CaseLessStringList(List[str]):
    """List that assumes all elements are lists and performs case less comparisons on them.

    Like a standard list this structure makes a copy of the existing data, while converting all entries to upper case
    strings.

    .. note:: All items added to this list are converted to upper case

    """

    def __init__(self, iterable: Iterable[str]):
        super().__init__(str(i).upper() for i in iterable)

    def __contains__(self, item: str):
        return super().__contains__(str(item).upper())

    def extend(self, iterable: Iterable[str]):
        return super().extend(str(i).upper() for i in iterable)

    def append(self, p_object: str):
        return super().append(str(p_object).upper())

    def insert(self, index: int, p_object: str):
        super().insert(index, str(p_object).upper())

    def index(self, value: str, *args, **kwargs) -> int:
        return super().index(str(value).upper(), *args, **kwargs)

    def remove(self, value: str):
        super().remove(str(value).upper())
