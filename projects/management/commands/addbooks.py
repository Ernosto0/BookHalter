from projects.models import Books
from django.db import IntegrityError

def add_books(book_list):
    for book in book_list:
        # Check if the book already exists
        if not Books.objects.filter(name=book['title'], author=book['author']).exists():
            try:
                Books.objects.create(name=book['title'], author=book['author'])
                print(f"Added book: {book['title']} by {book['author']}")
            except IntegrityError as e:
                print(f"An error occurred when adding '{book['title']}': {e}")
        else:
            print(f"Book already exists: {book['title']} by {book['author']}")
    