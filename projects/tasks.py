from django.db.models import Count
from .models import Books
from celery import shared_task

@shared_task
def cleanup_duplicates():
    # Find books with the same name and author
    duplicates = Books.objects.values('name', 'author') \
                      .annotate(name_count=Count('name'), author_count=Count('author')) \
                      .filter(name_count__gt=1, author_count__gt=1)

    for entry in duplicates:
        # For each set of duplicates, find individual book entries
        books = Books.objects.filter(name=entry['name'], author=entry['author']).order_by('-vote_total', 'created')

        # If there are duplicates, the first one is kept (highest votes or oldest), the rest are deleted
        if books.count() > 1:
            books_to_delete = books[1:]  # Exclude the first book from deletion
            books_to_delete.delete()

    print("Duplicate books cleanup complete.")