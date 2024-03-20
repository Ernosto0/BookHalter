from projects.models import Books
from django.db import IntegrityError
from fuzzywuzzy import process

def add_books(book_list):
    for book in book_list:
        valid_amazon_id = book['id_amazon'] if book['id_amazon'].isdigit() else None

        # Check if the book already exists (considering name and author for uniqueness)
        if not Books.objects.filter(name=book['title'], author=book['author']).exists():
            if not find_fuzzy_match(book['title'], book['author']):
                try:
                    # Create a new book entry with all provided details
                    Books.objects.create(
                        name=book['title'],
                        author=book['author'][0],
                        published_year=2100,
                        description=book['description'],
                        cover_image_url=book['cover_image'],
                        amazon_id=valid_amazon_id
                    )
                    print(f"Added book: {book['title']} by {book['author'][0]}")
                except IntegrityError as e:
                    print(f"An error occurred when adding '{book['title']}': {e}")
            else:
                print(f"Book already exists: {book['title']} by {book['author'][0]}")




def find_fuzzy_match(new_title, new_author, threshold=90):
    # Fetch titles and authors from the database
    books = Books.objects.values_list('name', 'author')

    # Check each book for a fuzzy match on both title and author
    for title, author in books:
        title_similarity = process.extractOne(new_title[0], [title])[1]  # type: ignore
        author_similarity = process.extractOne(new_author[0], [author])[1] # type: ignore

        # If both title and author match above the threshold, consider it a match
        if title_similarity > threshold and author_similarity > threshold:
            return True  # A fuzzy match was found

    return False  # No fuzzy match found