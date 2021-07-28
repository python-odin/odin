# -*- coding: utf-8 -*-
import enum
import uuid
from datetime import datetime
from typing import List, Optional

import odin
from odin.new_resource import NewResource, AbstractResource, Options


class Author(NewResource):
    name: str

    class Meta:
        name_space = None


class Publisher(NewResource):
    name: str

    class Meta:
        name_space = None


class LibraryBook(AbstractResource):
    class Meta:
        abstract = True
        name_space = "new_library"


class Book(LibraryBook):
    class Meta:
        key_field_name = "isbn"

    title: str
    isbn: str = Options(field_type=odin.StringField)
    num_pages: Optional[int]
    rrp: float = Options(20.4, use_default_if_not_provided=True)
    fiction: bool = Options(is_attribute=True)
    genre: str = Options(
        choices=(
            ("sci-fi", "Science Fiction"),
            ("fantasy", "Fantasy"),
            ("biography", "Biography"),
            ("others", "Others"),
            ("computers-and-tech", "Computers & technology"),
        ),
    )
    published: List[datetime]
    authors: List[Author] = Options(use_container=True)
    publisher: Optional[Publisher]

    A_CONST = "Foo Bar"

    def __eq__(self, other):
        if other:
            return vars(self) == vars(other)
        return False


class From(enum.Enum):
    Dumpster = "dumpster"
    Shop = "shop"
    Ebay = "ebay"


class IdentifiableBook(Book):
    id: uuid.UUID
    purchased_from: From
