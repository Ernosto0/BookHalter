from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Books
from django.core.cache import cache


@receiver(post_save, sender=Books)
@receiver(post_delete, sender=Books)
def clear_book_cache(sender, **kwargs):
    cache.delete('recommended_books')
