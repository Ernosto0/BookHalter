from projects.models import Books
from django.db import IntegrityError, transaction
from fuzzywuzzy import process, fuzz
import logging
import re


logger = logging.getLogger(__name__)


def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text

def log_duplicate_detection(title, author):
    logger.info(f"Potential duplicate detected: {title} by {author}")

def add_books(book_list):
    for book in book_list:
        try:
            if 'title' not in book or 'author' not in book or not book['author']:
                logger.error(f"Missing title or author for book: {book}")
                continue

            normalized_title= normalize_text(book['title'])
            normalized_author = normalize_text(book['author'][0])

            title = book['title']
            author = book['author'][0]

            if not Books.objects.filter(name=normalized_title, author=normalized_author).exists():
                if not find_fuzzy_match(normalized_title, normalized_author):
                    try:
                        with transaction.atomic():
                            Books.objects.create(
                                name=title,
                                author=author,
                                published_year=book.get('year', None),
                                description=book.get('description', ''),
                                cover_image_url=book.get('cover_image', ''),
                                googlebooks_link=book.get('googlebooks_link', ''),
                            )
                            logger.info(f"Added book: {book['title']} by {book['author'][0]}")
                    except IntegrityError as e:
                        logger.error(f"IntegrityError when adding '{book['title']}': {e}")
                else:
                    log_duplicate_detection(book['title'], book['author'][0])
                    logger.info(f"Book already exists: {book['title']} by {book['author'][0]}")
            else:
                logger.info(f"Book already exists in database: {book['title']} by {book['author'][0]}")
        except Exception as e:
            logger.error(f"An unexpected error occurred for book '{book.get('title', 'Unknown')}': {e}")
    



def find_fuzzy_match(new_title, new_author, threshold=90):
    try:
        books = Books.objects.values_list('name', 'author')
        
        for title, author in books:
            title_similarity = max(fuzz.token_sort_ratio(new_title, title), fuzz.token_set_ratio(new_title, title))
            author_similarity = max(fuzz.token_sort_ratio(new_author, author), fuzz.token_set_ratio(new_author, author))

            if title_similarity > threshold and author_similarity > threshold:
                return True

        return False
    except Exception as e:
        logger.error(f"An error occurred when finding a fuzzy match: {e}")
        return False
    

