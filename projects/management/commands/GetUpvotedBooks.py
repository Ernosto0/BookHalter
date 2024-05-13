from django.db.models import Subquery, OuterRef
from projects.models import Vote, Books # type: ignore

def get_upvoted_books_by_user(user_id):
    # Fetch the latest upvote IDs separately
    upvotes = Vote.objects.filter(user_id=user_id, vote_type='up').order_by('-created_at')[:2]
    upvote_ids = upvotes.values_list('id', flat=True)  # Retrieve upvote IDs

    # Query using the list of IDs, not a subquery
    upvoted_books_names = Books.objects.filter(vote__id__in=list(upvote_ids)).distinct().values_list('name', flat=True)

    return list(upvoted_books_names)
