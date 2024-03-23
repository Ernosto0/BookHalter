from django.contrib.auth.decorators import login_required
from users.models import UserBookData


def reset_user_vote_count(request):
    current_user = request.user

    try:
        # Access the UserBookData instance related to the current user
        user_book_data = current_user.book_data

        # Update the vote_count to 0
        user_book_data.vote_count = 0

        user_book_data.save()

        print("User vote count has been reset to 0.")
        return True  # You might want to return a suitable response or confirmation message

    except UserBookData.DoesNotExist:
        print("UserBookData does not exist for the current user.")
        return False  # Or return a suitable error response/message

    except Exception as e:
        print(f"An error occurred: {e}")
        return False  # Or return a suitable error response/message
    
def increase_vote_count(request):
    current_user = request.user
    try:
        user_book_data = current_user.book_data

        # Ensure vote_count is not None, initialize to 0 if None
        if user_book_data.vote_count is None:
            user_book_data.vote_count = 0

        user_book_data.vote_count += 1
        user_book_data.save()

        print("Vote count increased by 1.")
        return True

    except UserBookData.DoesNotExist:
        print("UserBookData does not exist for the given user ID.")
        return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def decrease_vote_count(request):
    current_user = request.user
    try:
        user_book_data = current_user.book_data

        # Ensure vote_count is not None, initialize to 0 if None
        if user_book_data.vote_count is None:
            user_book_data.vote_count = 0

        user_book_data.vote_count -= 1
        user_book_data.save()

        print("Vote count decreased by 1.")
        return True

    except UserBookData.DoesNotExist:
        print("UserBookData does not exist for the given user ID.")
        return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

