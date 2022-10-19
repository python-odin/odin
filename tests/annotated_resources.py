import enum
import uuid
from datetime import datetime
from typing import List, Optional

import odin
from odin.annotated_resource import Options


class Author(odin.AResource):
    name: str

    class Meta:
        namespace = None


class Publisher(odin.AResource):
    name: str

    class Meta:
        namespace = None


class LibraryBook(odin.AResource, abstract=True):
    class Meta:
        namespace = "new_library"


class Book(LibraryBook):
    class Meta:
        key_field_name = "isbn"

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


class From(enum.Enum):
    Dumpster = "dumpster"
    Shop = "shop"
    Ebay = "ebay"


class IdentifiableBook(Book):
    id: uuid.UUID
    purchased_from: From


class Subscriber(odin.AResource):
    name: str
    address: str


class Library(odin.AnnotatedResource):
    name: str
    books: List[LibraryBook]
    subscribers: Optional[Subscriber]

    @odin.calculated_field
    def book_count(self):
        return len(self.books)

    class Meta:
        namespace = "new_library"
