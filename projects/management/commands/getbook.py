from projects.models import Books

def search_books_in_database(books_to_search):
    found_books = []
    book = None
    for book_to_search in books_to_search:
        # Try to find the book in the database
        print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCccc")

        print(book_to_search['title'], book_to_search['author'][0])
        try:
            book = Books.objects.get(name__iexact=book_to_search['title'], author__iexact=book_to_search['author'][0])
            found_books.append(book)
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            print(book.description)
        except Books.DoesNotExist:
            
            print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
            
   
    return found_books