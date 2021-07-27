from datetime import date
from enum import Enum
from typing import List, Optional

from odin import new_resource
from odin.utils import getmeta
from .resources import Author, Publisher


class Genre(Enum):
    ScienceFiction = "sci-fi"
    Fantasy = "fantasy"
    Biography = "biography"
    Others = "others"
    ComputersAndTechnology = "computers-and-tech"


class BaseBook(new_resource.AbstractResource):
    title: str


class OldBook(new_resource.NewResource):
    title: str
    isbn: str


class NewBook(BaseBook):
    class Meta:
        key_field_name = "isbn"

    isbn: str
    num_pages: int
    rrp: float = new_resource.Options(20.4, use_default_if_not_provided=True)
    fiction: bool = new_resource.Options(is_attribute=True)
    genre: Genre = Genre.ScienceFiction
    published: List[date]
    authors: List[Author]
    publisher: Optional[Publisher]

    def __eq__(self, other):
        if other:
            return vars(self) == vars(other)
        return False


def test_meta():
    meta = getmeta(NewBook)

    assert meta.fields == []
