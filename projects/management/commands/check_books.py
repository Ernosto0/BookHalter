from django.db.models import Q
from projects.models import Books
from fuzzywuzzy import process, fuzz
import re

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
            if not find_fuzzy_match(book['title'], book['author']):
                new_books.append(book)  # If the book doesn't exist, add it to the new_books list

    print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
    print(new_books)
    return new_books

def find_fuzzy_match(new_title, new_author, threshold=99):
    books = Books.objects.values_list('name', 'author')
    new_title_processed = preprocess_text(new_title)
    new_author_processed = preprocess_text(new_author)

    for title, author in books:
        title_similarity = fuzz.token_set_ratio(new_title_processed, preprocess_text(title))
        author_similarity = fuzz.token_set_ratio(new_author_processed, preprocess_text(author))

        if title_similarity > threshold and author_similarity > threshold:
            return True  # A fuzzy match was found
    return False  # No fuzzy match found

def preprocess_text(text):
    # Remove punctuation and convert to lowercase
    return re.sub(r'[^\w\s]', '', text).lower()