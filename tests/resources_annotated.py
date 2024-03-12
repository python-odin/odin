import enum
import uuid
from datetime import datetime
from functools import cached_property
from typing import List, Optional

import odin
from odin.annotated_resource import Options
from odin.utils import snake_to_camel


class Author(odin.AResource):
    name: str

    class Meta:
        namespace = "annotated"


class Publisher(odin.AResource):
    name: str

    class Meta:
        namespace = "annotated"

    @cached_property
    def capitalised_name(self):
        return self.name.upper()


class LibraryBook(odin.AResource, abstract=True):
    class Meta:
        namespace = "annotated.new_library"


class Book(LibraryBook):
    class Meta:
        namespace = "annotated"
        key_field_name = "isbn"
        allow_field_shadowing = True

    title: str
    isbn: str = odin.Options(
        max_length=32,
    )
    num_pages: Optional[int]
    rrp: float = odin.Options(
        20.4,
        use_default_if_not_provided=True,
    )
    fiction: bool = True
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
    authors: List[Author] = odin.Options(
        use_container=True,
    )
    publisher: Optional[Publisher]

    A_CONST = "Foo Bar"

    def __eq__(self, other):
        if other:
            return vars(self) == vars(other)
        return False


class AltBook(Book):
    """A special case of book.

    This is a special case of book that has a limit on the length of the title.

    And to test overriding fields.
    """

    title: str = odin.Options(max_length=10)


class From(enum.Enum):
    Dumpster = "dumpster"
    Shop = "shop"
    Ebay = "ebay"


class IdentifiableBook(Book):
    id: uuid.UUID
    purchased_from: From


class Subscriber(odin.Resource):
    """Mixed resource types"""

    name: str = odin.StringField()
    address: str = odin.StringField()


class Library(odin.AnnotatedResource):
    name: str
    books: List[LibraryBook]
    subscribers: Optional[Subscriber]

    @odin.calculated_field
    def book_count(self):
        return len(self.books)

    class Meta:
        namespace = "annotated.new_library"


class CamelCaseResource(odin.AnnotatedResource):
    class Meta:
        namespace = "annotated.foo.bar"
        field_name_format = snake_to_camel

    full_name: str
    year_of_birth: str


class InheritedCamelCaseResource(CamelCaseResource):
    email_address: str
