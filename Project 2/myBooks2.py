from typing import Optional, List

from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()


class Book:
    def __init__(self, id: int, title: str, author: str, description: str,
                 rating: int, published_date: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(default=None, description="id is not need to "
                                                        "create a book")
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                'published_date': 2029
            }
        }
    }


BOOKS: List[Book] = [
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 5,
         2030),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5, 2030),
    Book(3, 'Master Endpoints', 'codingwithroby', 'A awesome book!', 5, 2029),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 2028),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 2027),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 2026)
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_books_by_published_date(published_date: int = Query(gt=1999,
                                                                   lt=2031)):
    books_to_return: list[Book] = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return


@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_books_by_rating(rating: int = Query(gt=0, lt=6)):
    books = []
    for book in BOOKS:
        if book.rating == rating:
            books.append(book)
    return books


@app.post("/create_book", status_code=status.HTTP_201_CREATED)
async def create_new_book(book_request: BookRequest):
    book: Book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(book))


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_request: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_request.id:
            BOOKS[i] = Book(**book_request.model_dump())
            return
    raise HTTPException(detail="Item not found", status_code=404)


@app.delete("/books/{book_to_delete}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_to_delete: int = Path(gt=0)):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_to_delete:
            BOOKS.pop(i)
            return
    raise HTTPException(detail="Item not found", status_code=404)
