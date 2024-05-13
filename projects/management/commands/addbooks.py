from projects.models import Books
from django.db import IntegrityError, transaction
from fuzzywuzzy import process 
import logging


logger = logging.getLogger(__name__)

def add_books(book_list):
    for book in book_list:
        try:
            if 'title' not in book or 'author' not in book or not book['author']:
                logger.error(f"Missing title or author for book: {book}")
                continue

            if not Books.objects.filter(name=book['title'], author=book['author'][0]).exists():
                if not find_fuzzy_match(book['title'], book['author'][0]):
                    try:
                        with transaction.atomic():
                            Books.objects.create(
                                name=book['title'],
                                author=book['author'][0],
                                published_year=book.get('year', None),
                                description=book.get('description', ''),
                                cover_image_url=book.get('cover_image', ''),
                                googlebooks_link=book.get('googlebooks_link', ''),
                            )
                            logger.info(f"Added book: {book['title']} by {book['author'][0]}")
                    except IntegrityError as e:
                        logger.error(f"IntegrityError when adding '{book['title']}': {e}")
                else:
                    logger.info(f"Book already exists: {book['title']} by {book['author'][0]}")
            else:
                logger.info(f"Book already exists in database: {book['title']} by {book['author'][0]}")
        except Exception as e:
            logger.error(f"An unexpected error occurred for book '{book.get('title', 'Unknown')}': {e}")




def find_fuzzy_match(new_title, new_author, threshold=99):
    
    try:
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
    except Exception as e:
        print(f"An error occurred when finding a fuzzy match: {e}")
        return False