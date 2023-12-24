from projects.models import Books
from django.db import IntegrityError

def add_books(book_list):
    for book in book_list:
        # Check if the book already exists
        if not Books.objects.filter(name=book[0], author=book[1]).exists():
            try:
                Books.objects.create(name=book[0], author=book[1])
                print(f"Added book: {book[0]} by {book[1]}")
            except IntegrityError as e:
                print(f"An error occurred when adding '{book[0]}': {e}")
        else:
            print(f"Book already exists: {book[0]} by {book[1]}")
    