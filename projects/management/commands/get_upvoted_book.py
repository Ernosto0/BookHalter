from projects.models import Vote, Books  # Replace 'your_app' with the name of your Django app

def get_upvoted_books_by_user(user_id):

    upvotes = Vote.objects.filter(user_id=user_id, vote_type='up')

    upvoted_books_names = Books.objects.filter(vote__in=upvotes).distinct().values_list('name', flat=True)

    return list(upvoted_books_names)

