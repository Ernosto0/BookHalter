from projects.models import Books
from django.db import IntegrityError

def add_books(book_list):
    for book in book_list:
        
        # Check if the book already exists (considering name and author for uniqueness)
        if not Books.objects.filter(name=book['name'], author=book['author']).exists():
            try:
                # Create a new book entry with all provided details
                Books.objects.create(
                    name=book['name'],
                    author=book['author'],
                    published_year=book['published_year'],
                    description=book['description'],
                    cover_image_url=book['featured_image_url'] 
                )
                print(f"Added book: {book['name']} by {book['author']}")
            except IntegrityError as e:
                print(f"An error occurred when adding '{book['name']}': {e}")
        else:
            print(f"Book already exists: {book['name']} by {book['author']}")
