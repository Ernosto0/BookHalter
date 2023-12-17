from projects.models import Books

def search_books_in_database(books_to_search):
    found_books = []
    for book_to_search in books_to_search:
        # Try to find the book in the database
        try:
            book = Books.objects.get(name__iexact=book_to_search['title'], author__iexact=book_to_search['author'])
            found_books.append(book)
        except Books.DoesNotExist:
            # If the book isn't found, you might want to handle it somehow
            pass
    return found_books