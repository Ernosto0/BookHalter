from projects.models import Books

def search_books_in_database(books_to_search):
    found_books = []
    for book_to_search in books_to_search:
        # Try to find the book in the database
        try:
            book = Books.objects.get(name__iexact=book_to_search[0], author__iexact=book_to_search[1])
            found_books.append(book)
        except Books.DoesNotExist:
            
            pass
    return found_books