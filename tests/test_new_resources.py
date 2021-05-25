from enum import Enum

from odin import new_resources


class Genre(Enum):
    ScienceFiction = "sci-fi"
    Fantasy = "fantasy"
    Biography = "biography"
    Others = "others"
    ComputersAndTechnology = "computers-and-tech"


class Book(new_resources.NewResource):
    class Meta:
        key_field_name = "isbn"

    title: str
    isbn: str
    num_pages: int
    rrp: float = 20.4
    fiction: bool
    genre: Genre
    published: List[datetime]
    authors: List[Author]
    publisher: Optional[Publisher] = None
