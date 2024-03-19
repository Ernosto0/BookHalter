from django.db.models import Q
from projects.models import Books

def remove_existing_books(book_data):
    """
    Removes books from the provided list that already exist in the database.

    Args:
    book_data (list): A list of dictionaries, each representing a book with 'title', 'author', and 'explanation'.

    Returns:
    list: A list of dictionaries representing books that do not exist in the database.
    """
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    print(book_data)

    new_books = []  # List to hold books that don't exist in the database

    for book in book_data:
        title = book.get('title')
        author = book.get('author')

        # Check if the book exists in the database
        if not Books.objects.filter(Q(name__iexact=book.get('title')) & Q(author__iexact=book.get('author'))).exists():
            new_books.append(book)  # If the book doesn't exist, add it to the new_books list
    print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
    print(new_books)
    return new_books

