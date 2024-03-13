from projects.models import Books
from django.db import IntegrityError

def add_books(book_list):
    for book in book_list:
        print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
        print(book_list)
        # Check if the book already exists (considering name and author for uniqueness)
        if not Books.objects.filter(name=book['title'], author=book['author']).exists():
            try:
                # Create a new book entry with all provided details
                Books.objects.create(
                    name=book['title'],
                    author=book['author'][0],
                    published_year=2100,
                    description=book['description'],
                    cover_image_url=book['cover_image'] 
                )
                print(f"Added book: {book['title']} by {book['author'][0]}")
            except IntegrityError as e:
                print(f"An error occurred when adding '{book['title']}': {e}")
        else:
            print(f"Book already exists: {book['title']} by {book['author'][0]}")
