from projects.models import Vote, Books

def get_upvoted_books_by_user(user_id):
    # Assuming 'created_at' is a field in your Vote model that records when the vote was made
    upvotes = Vote.objects.filter(user_id=user_id, vote_type='up').order_by('-created_at')[:2]

    upvoted_books_names = Books.objects.filter(vote__in=upvotes).distinct().values_list('name', flat=True)

    return list(upvoted_books_names)
